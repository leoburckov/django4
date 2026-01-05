from django.db import models
from django.core.exceptions import ValidationError


class Course(models.Model):
    """Course model."""

    title = models.CharField(max_length=200, verbose_name='Название курса')
    preview = models.ImageField(
        upload_to='course_previews/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        null=True,
        blank=True,
        related_name='owned_courses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Lesson model."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField(max_length=200, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    preview = models.ImageField(
        upload_to='lesson_previews/',
        verbose_name='Превью',
        blank=True,
        null=True
    )
    video_url = models.URLField(
        verbose_name='Ссылка на видео',
        blank=True,
        null=True,
        validators=[]  # Валидатор будет в сериализаторе
    )
    owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        null=True,
        blank=True,
        related_name='owned_lessons'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.title} - {self.course.title}'


class Subscription(models.Model):
    """Subscription model for course updates."""

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Одна подписка на курс для пользователя
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} подписан на {self.course.title}'

    def clean(self):
        """Validate subscription."""
        from django.core.exceptions import ValidationError
        # Проверяем, что пользователь не подписывается на свой же курс
        if self.course.owner == self.user:
            raise ValidationError('Нельзя подписаться на свой собственный курс')
