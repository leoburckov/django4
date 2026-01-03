from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Payment


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'city', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone', 'city'),
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'get_paid_item', 'amount', 'payment_method')
    list_filter = ('payment_method', 'payment_date', 'paid_course', 'paid_lesson')
    search_fields = ('user__email', 'paid_course__title', 'paid_lesson__title')
    readonly_fields = ('payment_date',)

    def get_paid_item(self, obj):
        if obj.paid_course:
            return f'Курс: {obj.paid_course.title}'
        elif obj.paid_lesson:
            return f'Урок: {obj.paid_lesson.title}'
        return 'Не указано'

    get_paid_item.short_description = 'Оплаченный предмет'


admin.site.register(User, CustomUserAdmin)
