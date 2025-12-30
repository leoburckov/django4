from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    paid_course_title = serializers.CharField(source='paid_course.title', read_only=True, allow_null=True)
    paid_lesson_title = serializers.CharField(source='paid_lesson.title', read_only=True, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'paid_course_title',
            'paid_lesson', 'paid_lesson_title',
            'amount', 'payment_method'
        ]
        read_only_fields = ['payment_date']
