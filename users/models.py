from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from courses.models import Course, Lesson


class UserManager(BaseUserManager):
    """Custom user manager for email authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email authentication."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone'), max_length=15, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Payment model for tracking user payments."""

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Наличные'
        TRANSFER = 'transfer', 'Перевод на счет'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')

    # Поля для оплаты курса или урока (одно из них должно быть заполнено)
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Оплаченный курс',
        blank=True,
        null=True
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Оплаченный урок',
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        if self.paid_course:
            return f'{self.user.email} - {self.paid_course.title} - {self.amount}'
        elif self.paid_lesson:
            return f'{self.user.email} - {self.paid_lesson.title} - {self.amount}'
        return f'{self.user.email} - {self.amount}'

    def clean(self):
        """Validate that either course or lesson is provided."""
        from django.core.exceptions import ValidationError
        if not self.paid_course and not self.paid_lesson:
            raise ValidationError('Должен быть указан либо курс, либо урок')
        if self.paid_course and self.paid_lesson:
            raise ValidationError('Можно указать только курс ИЛИ урок, не оба одновременно')