from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Course, Lesson, Payment
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    LessonSerializer,
    PaymentSerializer,
    PaymentCreateSerializer
)
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import json
from .services.stripe_service import StripeService


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для операций CRUD с курсами."""

    queryset = Course.objects.all()

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор в зависимости от действия."""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    @swagger_auto_schema(
        methods=['get'],
        operation_description="Получить список уроков для конкретного курса",
        responses={200: LessonSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Получить уроки для конкретного курса."""
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """View для получения списка уроков и создания нового урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Получить список всех уроков",
        responses={200: LessonSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый урок",
        request_body=LessonSerializer,
        responses={
            201: LessonSerializer,
            400: "Некорректные данные"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View для получения, обновления и удаления конкретного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Получить детальную информацию об уроке",
        responses={200: LessonSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Обновить информацию об уроке",
        request_body=LessonSerializer,
        responses={200: LessonSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частично обновить информацию об уроке",
        request_body=LessonSerializer,
        responses={200: LessonSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удалить урок",
        responses={204: "Урок удален"}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PaymentListCreateView(generics.ListCreateAPIView):
    """View для получения списка платежей и создания нового платежа."""

    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    @swagger_auto_schema(
        operation_description="Получить список всех платежей",
        responses={200: PaymentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новый платеж для курса",
        request_body=PaymentCreateSerializer,
        responses={
            201: PaymentSerializer,
            400: "Некорректные данные"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PaymentRetrieveView(generics.RetrieveAPIView):
    """View для получения информации о конкретном платеже."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Получить детальную информацию о платеже",
        responses={200: PaymentSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """View for handling Stripe webhooks."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = StripeService.verify_webhook_signature(payload, sig_header)
        except ValidationError as e:
            return HttpResponse(str(e), status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_session_completed(session)
        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']
            self.handle_checkout_session_completed(session)
        elif event['type'] == 'checkout.session.async_payment_failed':
            session = event['data']['object']
            self.handle_checkout_session_failed(session)

        return HttpResponse(status=200)

    def handle_checkout_session_completed(self, session):
        """Handle completed checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session['id'])
            payment.status = 'succeeded'
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.save()
        except Payment.DoesNotExist:
            pass

    def handle_checkout_session_failed(self, session):
        """Handle failed checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session['id'])
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            pass


class PaymentSuccessView(APIView):
    """View for successful payment redirect."""

    permission_classes = []

    def get(self, request):
        return HttpResponse("""
        <html>
        <head>
            <title>Оплата успешна</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
                .success { color: green; font-size: 24px; }
            </style>
        </head>
        <body>
            <div class="success">✅ Оплата успешно завершена!</div>
            <p>Спасибо за покупку. Вы получите доступ к курсу в ближайшее время.</p>
            <a href="/">Вернуться на главную</a>
        </body>
        </html>
        """)


class PaymentCancelView(APIView):
    """View for canceled payment redirect."""

    permission_classes = []

    def get(self, request):
        return HttpResponse("""
        <html>
        <head>
            <title>Оплата отменена</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; }
                .cancel { color: orange; font-size: 24px; }
            </style>
        </head>
        <body>
            <div class="cancel">⚠️ Оплата отменена</div>
            <p>Вы можете попробовать оплатить курс позже.</p>
            <a href="/">Вернуться на главную</a>
        </body>
        </html>
        """)