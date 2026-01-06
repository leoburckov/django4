from django.db import models
from django.contrib.auth import get_user_model  # Используем этот метод!

User = get_user_model()  # Получаем модель пользователя динамически


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.title} - {self.course.title}'


class Payment(models.Model):
    """Payment model for course purchases."""

    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'Обрабатывается'),
        ('succeeded', 'Оплачено'),
        ('failed', 'Не удалось'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    course = models.ForeignKey(
        'Course',  # Используем строковую ссылку
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Курс'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    stripe_product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe'
    )
    stripe_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID сессии в Stripe'
    )
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID платежа в Stripe'
    )
    payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.course.title} - {self.amount}'