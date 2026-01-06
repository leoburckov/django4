from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Документация API
schema_view = get_schema_view(
    openapi.Info(
        title="Django LMS API",
        default_version='v1',
        description="API системы управления обучением",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@lms.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


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

        <h2>📚 Документация API:</h2>
        <ul>
            <li><a href="/swagger/">📖 Swagger UI</a> - интерактивная документация</li>
            <li><a href="/redoc/">📘 ReDoc</a> - альтернативная документация</li>
        </ul>

        <h2>🔧 Основные эндпоинты:</h2>
        <ul>
            <li><a href="/api/courses/">📖 Курсы</a></li>
            <li><a href="/api/lessons/">📝 Уроки</a></li>
            <li><a href="/api/payments/">💳 Платежи</a> (новое)</li>
            <li><a href="/admin/">⚙️ Админ-панель</a></li>
        </ul>
    </body>
    </html>
    """)


urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('courses.urls')),

    # Документация
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)