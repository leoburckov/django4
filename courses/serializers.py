from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Payment, Subscription
from .services.stripe_service import StripeService

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""

    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "course",
            "course_title",
            "amount",
            "status",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "amount",
            "status",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
            "created_at",
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""

    class Meta:
        model = Payment
        fields = ["course"]

    def validate(self, attrs):
        """Validate payment data."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("User is not authenticated")

        course = attrs.get("course")
        if not course.price or course.price <= 0:
            raise serializers.ValidationError("Course cannot be free")

        return attrs

    def create(self, validated_data):
        """Create payment and Stripe checkout session."""
        request = self.context.get("request")
        user = request.user
        course = validated_data["course"]

        # Create Stripe product
        product_id = StripeService.create_product(
            name=course.title,
            description=course.description or "",
        )

        # Create Stripe price
        price_id = StripeService.create_price(
            product_id=product_id,
            amount=float(course.price),
            currency="rub",
        )

        # Create Stripe checkout session
        success_url = f'{request.build_absolute_uri("/")}api/payments/success/'
        cancel_url = f'{request.build_absolute_uri("/")}api/payments/cancel/'

        session_data = StripeService.create_checkout_session(
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "payment_type": "course_purchase",
                "course_id": str(course.id),
                "user_id": str(user.id),
            },
        )

        # Create payment record
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=course.price,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data["session_id"],
            stripe_payment_intent_id=session_data.get("payment_intent_id"),
            payment_url=session_data["payment_url"],
            status=Payment.STATUS_PENDING,
        )

        return payment


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id',
            'user',
            'user_email',
            'course',
            'course_title',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['user', 'is_active', 'created_at']