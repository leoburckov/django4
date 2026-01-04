from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def home_view(request):
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
            .public { color: green; }
            .protected { color: orange; }
        </style>
    </head>
    <body>
        <h1>🎓 Django LMS API with JWT & Permissions</h1>

        <h2>🔐 Аутентификация (публичные):</h2>
        <ul>
            <li class="public"><a href="/api/users/register/">📝 Регистрация</a> - <code>POST /api/users/register/</code></li>
            <li class="public"><a href="/api/users/login/">🔑 Вход</a> - <code>POST /api/users/login/</code></li>
            <li class="public"><a href="/api/token/">🔑 Получить JWT токен</a> - <code>POST /api/token/</code></li>
            <li class="public"><a href="/api/token/refresh/">🔄 Обновить токен</a> - <code>POST /api/token/refresh/</code></li>
        </ul>

        <h2>📚 API эндпоинты (требуется авторизация):</h2>
        <ul>
            <li class="protected"><a href="/api/courses/">📖 Курсы</a> - <code>GET /api/courses/</code></li>
            <li class="protected"><a href="/api/lessons/">📝 Уроки</a> - <code>GET /api/lessons/</code></li>
            <li class="protected"><a href="/api/payments/">💰 Платежи</a> - <code>GET /api/payments/</code></li>
            <li class="protected"><a href="/api/users/profile/">👤 Профиль</a> - <code>GET /api/users/profile/</code></li>
        </ul>

        <h2>👥 Права доступа:</h2>
        <ul>
            <li><strong>Обычные пользователи:</strong> могут создавать/редактировать/удалять только свои курсы и уроки</li>
            <li><strong>Модераторы:</strong> могут просматривать/редактировать все курсы и уроки, но не могут создавать/удалять</li>
            <li><strong>Все эндпоинты</strong> (кроме регистрации/входа) требуют JWT токен</li>
        </ul>

        <h2>🛠 Использование:</h2>
        <ol>
            <li>Зарегистрируйтесь: <code>POST /api/users/register/</code></li>
            <li>Войдите: <code>POST /api/users/login/</code> (получите токен)</li>
            <li>Используйте токен: <code>Authorization: Bearer ваш_токен</code></li>
            <li>Тестируйте права доступа разными пользователями</li>
        </ol>

        <p><a href="/admin/">⚙️ Админ-панель</a></p>
    </body>
    </html>
    """
    return Response({"message": "Django LMS API", "docs": "See HTML response"})
    # Если хотите вернуть HTML, используйте:
    # from django.http import HttpResponse
    # return HttpResponse(html)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),

    # JWT authentication (public)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API routes (protected)
    path('api/', include('courses.urls')),
    path('api/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)