from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Course, Lesson, Payment, Subscription
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    SubscriptionSerializer,
)
from .services.stripe_service import StripeService
from .tasks import send_course_update_notification, send_lesson_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Course model.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_update(self, serializer):
        """Send notifications after course update."""
        instance = serializer.save()
        # Trigger async notification task
        send_course_update_notification.delay(instance.id)

    @swagger_auto_schema(
        method='get',
        operation_description='Get all lessons for specific course',
        responses={
            200: LessonSerializer(many=True),
            404: 'Course not found'
        }
    )
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """
        Get lessons for specific course.
        """
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_description='Subscribe to course updates',
        responses={
            201: 'Subscribed successfully',
            400: 'Already subscribed'
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Subscribe to course updates."""
        course = self.get_object()
        user = request.user

        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course,
            defaults={'is_active': True}
        )

        if not created and subscription.is_active:
            return Response(
                {'detail': 'Already subscribed to this course'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.is_active = True
        subscription.save()

        return Response(
            {'detail': 'Successfully subscribed to course updates'},
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        method='post',
        operation_description='Unsubscribe from course updates',
        responses={
            200: 'Unsubscribed successfully',
            404: 'Subscription not found'
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, pk=None):
        """Unsubscribe from course updates."""
        course = self.get_object()
        user = request.user

        try:
            subscription = Subscription.objects.get(user=user, course=course)
            subscription.is_active = False
            subscription.save()
            return Response(
                {'detail': 'Successfully unsubscribed from course updates'}
            )
        except Subscription.DoesNotExist:
            return Response(
                {'detail': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class LessonListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating lessons.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        """Send notifications after lesson creation."""
        instance = serializer.save()
        # Trigger async notification task
        send_lesson_update_notification.delay(instance.id)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating and deleting a lesson.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_update(self, serializer):
        """Send notifications after lesson update."""
        instance = serializer.save()
        # Trigger async notification task
        send_lesson_update_notification.delay(instance.id)


# ДОБАВЛЯЕМ ОТСУТСТВУЮЩИЕ КЛАССЫ:

class PaymentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating payments.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Set current user as payment owner."""
        serializer.save(user=self.request.user)


class PaymentRetrieveView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving payment details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)


class SubscriptionListView(generics.ListAPIView):
    """
    API endpoint for listing user's subscriptions.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """Return subscriptions for current user."""
        return Subscription.objects.filter(
            user=self.request.user,
            is_active=True
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Webhook endpoint for Stripe events.
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description='Handle Stripe webhook events',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING),
                'type': openapi.Schema(type=openapi.TYPE_STRING),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        ),
        responses={
            200: 'Webhook processed successfully',
            400: 'Invalid webhook signature',
        }
    )
    def post(self, request):
        """Handle Stripe webhook."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            # Verify webhook signature
            import stripe
            from django.conf import settings

            stripe.api_key = settings.STRIPE_SECRET_KEY

            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_session_completed(session)
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            self._handle_checkout_session_expired(session)

        return JsonResponse({'status': 'success'})

    def _handle_checkout_session_completed(self, session):
        """Handle completed checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session['id'])
            payment.status = Payment.STATUS_SUCCEEDED
            payment.stripe_payment_intent_id = session.get('payment_intent')
            payment.save()
        except Payment.DoesNotExist:
            pass

    def _handle_checkout_session_expired(self, session):
        """Handle expired checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session['id'])
            payment.status = Payment.STATUS_CANCELED
            payment.save()
        except Payment.DoesNotExist:
            pass


class PaymentSuccessView(APIView):
    """
    Success page for payment redirect.
    """

    permission_classes = []

    def get(self, request):
        """Return success message."""
        return JsonResponse({
            'status': 'success',
            'message': 'Payment completed successfully',
        })


class PaymentCancelView(APIView):
    """
    Cancel page for payment redirect.
    """

    permission_classes = []

    def get(self, request):
        """Return cancel message."""
        return JsonResponse({
            'status': 'canceled',
            'message': 'Payment was canceled',
        })