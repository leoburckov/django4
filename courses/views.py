from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Course, Lesson, Subscription
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    LessonSerializer
)


from users.permissions import CourseLessonPermission
from .paginators import CoursePagination, LessonPagination

from rest_framework import serializers


class SubscriptionSerializer(serializers.ModelSerializer):
    """Локальный сериализатор для Subscription."""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'user_email', 'course', 'course_title', 'created_at']
        read_only_fields = ['created_at']


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course."""

    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]
    pagination_class = CoursePagination

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['owner', 'created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        paginator = LessonPagination()
        paginated_lessons = paginator.paginate_queryset(lessons, request)
        serializer = LessonSerializer(paginated_lessons, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        course = self.get_object()
        user = request.user

        if course.owner == user:
            return Response(
                {'error': 'Нельзя подписаться на свой собственный курс'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            'message': message,
            'subscribed': subscribed,
            'course_id': course.id,
            'course_title': course.title
        })

    @action(detail=False, methods=['get'])
    def subscribed(self, request):
        user = request.user
        subscribed_courses = Course.objects.filter(subscriptions__user=user)
        page = self.paginate_queryset(subscribed_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscribed_courses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        user = request.user
        my_courses = Course.objects.filter(owner=user)
        page = self.paginate_queryset(my_courses)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(my_courses, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """View для получения списка уроков и создания нового урока."""

    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]
    pagination_class = LessonPagination

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['course', 'owner', 'created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Lesson.objects.all()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        owner_id = self.request.query_params.get('owner_id')
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View для получения, обновления и удаления конкретного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]


class SubscriptionAPIView(APIView):
    """API View для управления подписками на курсы."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        paginator = CoursePagination()
        paginated_subscriptions = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(paginated_subscriptions, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {'error': 'Параметр course_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if course.owner == user:
            return Response(
                {'error': 'Нельзя подписаться на свой собственный курс'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            'message': message,
            'subscribed': subscribed,
            'course_id': course_id,
            'course_title': course.title
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Подписка/отписка на обновления курса."""
        course = self.get_object()
        user = request.user

        # Проверяем, является ли пользователь владельцем курса
        if course.owner == user:
            return Response(
                {'error': 'Нельзя подписаться на свой собственный курс'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем существующую подписку
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Удаляем подписку (отписываемся)
            subscription.delete()
            message = 'Подписка удалена'
            subscribed = False
        else:
            # Создаем подписку
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            subscribed = True

        return Response({
            'message': message,
            'subscribed': subscribed,
            'course_id': course.id,
            'course_title': course.title
        })