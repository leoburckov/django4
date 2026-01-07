from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Course, Lesson, Payment
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    @swagger_auto_schema(
        method="get",
        operation_description="Get all lessons for specific course",
        responses={200: LessonSerializer(many=True), 404: "Course not found"},
    )
    @action(detail=True, methods=["get"])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == "POST":
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        """Set current user as payment owner."""
        serializer.save(user=self.request.user)


class PaymentRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """Return payments for current user."""
        return Payment.objects.filter(user=self.request.user)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Handle Stripe webhook events",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_STRING),
                "type": openapi.Schema(type=openapi.TYPE_STRING),
                "data": openapi.Schema(type=openapi.TYPE_OBJECT),
            },
        ),
        responses={
            200: "Webhook processed successfully",
            400: "Invalid webhook signature",
        },
    )
    def post(self, request):
        """Handle Stripe webhook."""
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

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
            return JsonResponse({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._handle_checkout_session_completed(session)
        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            self._handle_checkout_session_expired(session)

        return JsonResponse({"status": "success"})

    def _handle_checkout_session_completed(self, session):
        """Handle completed checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session["id"])
            payment.status = Payment.STATUS_SUCCEEDED
            payment.stripe_payment_intent_id = session.get("payment_intent")
            payment.save()
        except Payment.DoesNotExist:
            pass

    def _handle_checkout_session_expired(self, session):
        """Handle expired checkout session."""
        try:
            payment = Payment.objects.get(stripe_session_id=session["id"])
            payment.status = Payment.STATUS_CANCELED
            payment.save()
        except Payment.DoesNotExist:
            pass


class PaymentSuccessView(APIView):
    permission_classes = []

    def get(self, request):
        """Return success message."""
        return JsonResponse(
            {
                "status": "success",
                "message": "Payment completed successfully",
            }
        )


class PaymentCancelView(APIView):
    permission_classes = []

    def get(self, request):
        """Return cancel message."""
        return JsonResponse(
            {
                "status": "canceled",
                "message": "Payment was canceled",
            }
        )
