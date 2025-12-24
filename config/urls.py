from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


# Простое представление для корневого URL
def home_view(request):
    return HttpResponse("""
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
        <p>Добро пожаловать в систему управления обучением!</p>

        <h2>📚 Доступные API-эндпоинты:</h2>
        <ul>
            <li><a href="/api/courses/">📖 Список курсов</a> - <code>GET /api/courses/</code></li>
            <li><a href="/api/lessons/">📝 Список уроков</a> - <code>GET /api/lessons/</code></li>
            <li><a href="/admin/">⚙️ Админ-панель</a> - <code>/admin/</code></li>
            <li><a href="/api-auth/login/">🔐 API аутентификация</a> - <code>/api-auth/login/</code></li>
        </ul>

        <h2>🛠 Использование с Postman:</h2>
        <ul>
            <li>Создание курса: <code>POST /api/courses/</code></li>
            <li>Создание урока: <code>POST /api/lessons/</code></li>
            <li>Получение курса: <code>GET /api/courses/1/</code></li>
            <li>Обновление урока: <code>PUT /api/lessons/1/</code></li>
            <li>Удаление урока: <code>DELETE /api/lessons/1/</code></li>
        </ul>

        <p>Для работы с API используйте Postman или другой HTTP-клиент.</p>
    </body>
    </html>
    """)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('courses.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
