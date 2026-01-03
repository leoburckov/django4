from django.db import models


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
        'users.User',  # Используем строковую ссылку вместо импорта
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
    video_url = models.URLField(verbose_name='Ссылка на видео', blank=True, null=True)
    owner = models.ForeignKey(
        'users.User',  # Используем строковую ссылку вместо импорта
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