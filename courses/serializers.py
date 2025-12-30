from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for Course list view."""

    # Задание 1: Добавляем поле количества уроков через SerializerMethodField
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description',
                  'lessons_count', 'created_at']

    def get_lessons_count(self, obj):
        """Get count of lessons for the course."""
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for Course detail view."""

    # Задание 1: Добавляем и здесь для детального просмотра
    lessons_count = serializers.SerializerMethodField()

    # Задание 3: Добавляем вывод уроков через связанный сериализатор
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        """Get count of lessons for the course."""
        return obj.lessons.count()
