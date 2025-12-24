from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Lesson
from .serializers import CourseListSerializer, CourseDetailSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model CRUD operations."""

    queryset = Course.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get lessons for specific course."""
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonListCreateView(generics.ListCreateAPIView):
    """View for listing and creating lessons."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating and deleting a lesson."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer