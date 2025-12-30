from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def home_view(request):
    from django.http import HttpResponse
    html = """
    <html>
    <head>
        <title>Django LMS API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🎓 Django LMS API</h1>

        <h2>📚 Доступные API-эндпоинты:</h2>
        <ul>
            <li><a href="/api/courses/">📖 Список курсов</a></li>
            <li><a href="/api/lessons/">📝 Список уроков</a></li>
            <li><a href="/api/payments/">💰 Список платежей</a></li>
            <li><a href="/admin/">⚙️ Админ-панель</a></li>
        </ul>

        <h2>🔍 Фильтрация платежей:</h2>
        <ul>
            <li><code>/api/payments/?ordering=payment_date</code> - сортировка по дате</li>
            <li><code>/api/payments/?ordering=-payment_date</code> - сортировка по дате (по убыванию)</li>
            <li><code>/api/payments/?paid_course=1</code> - фильтр по курсу</li>
            <li><code>/api/payments/?paid_lesson=1</code> - фильтр по уроку</li>
            <li><code>/api/payments/?payment_method=transfer</code> - фильтр по способу оплаты</li>
            <li><code>/api/payments/?payment_date__gte=2024-01-01</code> - с даты</li>
        </ul>
    </body>
    </html>
    """
    return HttpResponse(html)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('users.urls')),  # добавляем маршруты для users
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
