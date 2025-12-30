from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for Payment model with filtering and ordering."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Задание 4: Настраиваем фильтрацию и сортировку
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    # Фильтрация по конкретным полям
    filterset_fields = {
        'paid_course': ['exact'],
        'paid_lesson': ['exact'],
        'payment_method': ['exact'],
        'payment_date': ['gte', 'lte', 'exact'],
    }

    # Поиск по связанным полям
    search_fields = [
        'user__email',
        'paid_course__title',
        'paid_lesson__title',
    ]

    # Сортировка
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']  # сортировка по умолчанию

    def get_queryset(self):
        """Optionally filter by course or lesson query parameters."""
        queryset = super().get_queryset()

        # Дополнительная фильтрация через query params
        course_id = self.request.query_params.get('course_id')
        lesson_id = self.request.query_params.get('lesson_id')

        if course_id:
            queryset = queryset.filter(paid_course_id=course_id)
        if lesson_id:
            queryset = queryset.filter(paid_lesson_id=lesson_id)

        return queryset
    