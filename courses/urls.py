from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonListCreateView,
    LessonRetrieveUpdateDestroyView,
    PaymentListCreateView,
    PaymentRetrieveView,
    StripeWebhookView,
    PaymentSuccessView,
    PaymentCancelView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Lessons endpoints
    path("lessons/", LessonListCreateView.as_view(), name="lesson-list"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyView.as_view(),
        name="lesson-detail",
    ),
    # Payments endpoints
    path("payments/", PaymentListCreateView.as_view(), name="payment-list"),
    path("payments/<int:pk>/", PaymentRetrieveView.as_view(), name="payment-detail"),
    # Stripe endpoints
    path("payments/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("payments/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
