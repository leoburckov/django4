from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""

    class Meta:
        model = Lesson
        fields = '__all__'


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