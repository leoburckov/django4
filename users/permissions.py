from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        # Разрешаем все методы для модераторов
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта поле owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
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

        return False


class IsNotModerator(permissions.BasePermission):
    """Проверяет, что пользователь НЕ является модератором."""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()