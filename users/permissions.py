from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Для User модели
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем или модератором."""

    def has_object_permission(self, request, view, obj):
        # Если пользователь модератор - разрешаем
        if request.user.groups.filter(name='moderators').exists():
            return True

        # Если пользователь владелец - разрешаем
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id

        return False


class IsNotModerator(permissions.BasePermission):
    """Проверяет, что пользователь НЕ является модератором."""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()


class IsOwnerOrModeratorOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование только владельцам и модераторам."""

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Модераторы могут редактировать
        if request.user.groups.filter(name='moderators').exists():
            return request.method != 'DELETE'  # Модераторы не могут удалять

        # Владельцы могут все
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False


class CourseLessonPermission(permissions.BasePermission):
    """Общие права для курсов и уроков."""

    def has_permission(self, request, view):
        # Разрешаем просмотр всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Создавать могут только не-модераторы
        if request.method == 'POST':
            return (request.user.is_authenticated and
                    not request.user.groups.filter(name='moderators').exists())

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Разрешаем просмотр всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Модераторы могут только редактировать, но не удалять
        if request.user.groups.filter(name='moderators').exists():
            return request.method in ['PUT', 'PATCH']

        # Владельцы могут все
        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False