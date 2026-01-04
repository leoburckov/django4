from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Lesson
from .serializers import CourseListSerializer, CourseDetailSerializer, LessonSerializer
from users.permissions import IsOwner, IsModerator, IsNotModerator, CourseLessonPermission


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model with proper permissions."""

    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def perform_create(self, serializer):
        """Automatically set owner when creating a course."""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Filter queryset for non-moderators."""
        user = self.request.user

        # Модераторы видят все
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()

        # Обычные пользователи видят все для чтения
        # Но при редактировании проверяется в has_object_permission
        return Course.objects.all()

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get lessons for specific course."""
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """View for listing and creating lessons with permissions."""

    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]

    def get_queryset(self):
        """Filter lessons based on user permissions."""
        user = self.request.user

        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()

        # Обычные пользователи видят все для чтения
        return Lesson.objects.all()

    def perform_create(self, serializer):
        """Automatically set owner when creating a lesson."""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a lesson with permissions."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, CourseLessonPermission]