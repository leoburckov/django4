from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from users.models import User, Payment
from courses.models import Course, Lesson
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test data: moderators group, users, courses, lessons, payments'

    def handle(self, *args, **kwargs):
        # 1. Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name='moderators')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа модераторов создана'))

        # 2. Создаем тестовых пользователей
        # Модератор
        moderator, m_created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={
                'first_name': 'Модератор',
                'last_name': 'Админов',
                'password': 'moderator123'
            }
        )
        if m_created:
            moderator.groups.add(moderators_group)
            self.stdout.write(self.style.SUCCESS('Создан модератор'))

        # Обычный пользователь
        user, u_created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'first_name': 'Обычный',
                'last_name': 'Пользователь',
                'password': 'user123'
            }
        )
        if u_created:
            self.stdout.write(self.style.SUCCESS('Создан обычный пользователь'))

        # 3. Создаем курсы
        course1, c1_created = Course.objects.get_or_create(
            title='Python для начинающих',
            defaults={
                'description': 'Основы программирования на Python',
                'owner': user  # Принадлежит обычному пользователю
            }
        )

        course2, c2_created = Course.objects.get_or_create(
            title='Django и DRF',
            defaults={
                'description': 'Создание веб-приложений с Django',
                'owner': moderator  # Принадлежит модератору
            }
        )

        if c1_created or c2_created:
            self.stdout.write(self.style.SUCCESS('Созданы курсы'))

        # 4. Создаем уроки
        lesson1, l1_created = Lesson.objects.get_or_create(
            course=course1,
            title='Введение в Python',
            defaults={
                'description': 'Основные понятия и синтаксис',
                'video_url': 'https://youtube.com/watch?v=example1',
                'owner': user  # Принадлежит обычному пользователю
            }
        )

        lesson2, l2_created = Lesson.objects.get_or_create(
            course=course2,
            title='Основы Django',
            defaults={
                'description': 'Создание первого проекта',
                'video_url': 'https://youtube.com/watch?v=example2',
                'owner': moderator  # Принадлежит модератору
            }
        )

        if l1_created or l2_created:
            self.stdout.write(self.style.SUCCESS('Созданы уроки'))

        # 5. Создаем платежи
        payments_data = [
            {'user': user, 'paid_course': course1, 'amount': Decimal('10000.00'), 'method': 'transfer'},
            {'user': user, 'paid_lesson': lesson1, 'amount': Decimal('2000.00'), 'method': 'cash'},
            {'user': moderator, 'paid_course': course2, 'amount': Decimal('15000.00'), 'method': 'transfer'},
        ]

        created_payments = 0
        for data in payments_data:
            payment, p_created = Payment.objects.get_or_create(
                user=data['user'],
                paid_course=data.get('paid_course'),
                paid_lesson=data.get('paid_lesson'),
                defaults={
                    'amount': data['amount'],
                    'payment_method': data['method']
                }
            )
            if p_created:
                created_payments += 1

        if created_payments > 0:
            self.stdout.write(self.style.SUCCESS(f'Создано {created_payments} платежей'))

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы!'))
        self.stdout.write('\nДанные для тестирования:')
        self.stdout.write('1. Модератор: moderator@example.com / moderator123')
        self.stdout.write('2. Обычный пользователь: user@example.com / user123')
        self.stdout.write('3. Курсы и уроки принадлежат разным пользователям')