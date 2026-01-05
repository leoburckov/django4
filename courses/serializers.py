from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeURLValidator, validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model."""

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            YouTubeURLValidator(field='video_url'),
        ]

    # Альтернативный вариант с функцией-валидатором
    # video_url = serializers.URLField(validators=[validate_youtube_url])


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for Course list view."""

    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description',
            'lessons_count', 'created_at', 'owner', 'is_subscribed'
        ]

    def get_lessons_count(self, obj):
        """Get count of lessons for the course."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Check if current user is subscribed to the course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for Course detail view."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        """Get count of lessons for the course."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Check if current user is subscribed to the course."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False


    class SubscriptionSerializer(serializers.ModelSerializer):
        """Serializer for Subscription model."""

        user_email = serializers.EmailField(source='user.email', read_only=True)
        course_title = serializers.CharField(source='course.title', read_only=True)

        class Meta:
            model = Subscription
            fields = ['id', 'user', 'user_email', 'course', 'course_title', 'created_at']
            read_only_fields = ['created_at']