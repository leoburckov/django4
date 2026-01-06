from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Payment
from .services.stripe_service import StripeService
from django.conf import settings
from django.core.validators import URLValidator

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""

    class Meta:
        model = Lesson
        fields = '__all__'
        # Убираем несуществующий YouTubeURLValidator, используем стандартный
        extra_kwargs = {
            'video_url': {
                'validators': [URLValidator()],  # Стандартный валидатор URL
            }
        }


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for Course list view."""

    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'created_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for Course detail view."""

    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'user_email',
            'course',
            'course_title',
            'amount',
            'status',
            'stripe_product_id',
            'stripe_price_id',
            'stripe_session_id',
            'payment_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'status',
            'stripe_product_id',
            'stripe_price_id',
            'stripe_session_id',
            'payment_url',
            'created_at',
            'updated_at',
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments."""

    class Meta:
        model = Payment
        fields = ['course']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        if not user or not user.is_authenticated:
            raise serializers.ValidationError('Пользователь не аутентифицирован')

        course = validated_data['course']

        # Создаем продукт в Stripe
        product_id = StripeService.create_product(
            name=course.title,
            description=course.description
        )

        # Создаем цену в Stripe
        # Для примера установим фиксированную цену 1000 рублей
        price_amount = 1000.00  # Можно брать из курса, если добавить поле price
        price_id = StripeService.create_price(
            product_id=product_id,
            amount=price_amount,
            currency='rub'
        )

        # Создаем сессию оплаты
        success_url = settings.STRIPE_SUCCESS_URL
        cancel_url = settings.STRIPE_CANCEL_URL

        session_data = StripeService.create_checkout_session(
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'payment_type': 'course_purchase',
                'course_id': str(course.id),
                'user_id': str(user.id),
            }
        )

        # Создаем запись о платеже
        payment = Payment.objects.create(
            user=user,
            course=course,
            amount=price_amount,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data['session_id'],
            stripe_payment_intent_id=session_data.get('payment_intent_id'),
            payment_url=session_data['payment_url'],
            status='pending'
        )

        return payment