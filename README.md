# Проект онлайн-обучения на Django DRF

Проект системы онлайн-обучения с использованием Django REST Framework.

## 📦 Технологии
- Django 6.0 + Django REST Framework
- PostgreSQL
- Redis + Celery
- Docker + Docker Compose
- Gunicorn

## 🚀 Быстрый запуск

### 1. Установите Docker и Docker Compose
Убедитесь, что у вас установлены:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### 2. Создайте файл настроек
Создайте файл `.env` в корне проекта:

```bash
# Если есть пример файла
cp .env.example .env

# Или создайте вручную
cat > .env << EOF
SECRET_KEY=ваш-секретный-ключ
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=drf_db
DB_USER=drf_user
DB_PASSWORD=drf_password
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
EOF