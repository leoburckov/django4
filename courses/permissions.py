from rest_framework import permissions
from users.permissions import IsModerator, IsOwner


class CoursePermissions(permissions.BasePermission):
    """Кастомные разрешения для курсов."""

    def has_permission(self, request, view):
        # Разрешаем просмотр списка всем авторизованным
        if view.action in ['list', 'retrieve']:
            return True

        # Разрешаем создание только не-модераторам
        if view.action == 'create':
            return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()

        # Для остальных действий нужна аутентификация
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модераторы могут просматривать и редактировать, но не удалять
        if request.user.groups.filter(name='moderators').exists():
            if view.action in ['retrieve', 'update', 'partial_update']:
                return True
            if view.action == 'destroy':
                return False

        # Владельцы могут все
        if obj.owner == request.user:
            return True

        # Для просмотра разрешаем всем авторизованным
        if view.action == 'retrieve':
            return request.user.is_authenticated

        return False


class LessonPermissions(permissions.BasePermission):
    """Кастомные разрешения для уроков."""

    def has_permission(self, request, view):
        # Разрешаем просмотр списка всем авторизованным
        if view.action in ['list', 'retrieve']:
            return True

        # Разрешаем создание только не-модераторам
        if view.action == 'create':
            return request.user.is_authenticated and not request.user.groups.filter(name='moderators').exists()

        # Для остальных действий нужна аутентификация
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Модераторы могут просматривать и редактировать, но не удалять
        if request.user.groups.filter(name='moderators').exists():
            if view.action in ['retrieve', 'update', 'partial_update']:
                return True
            if view.action == 'destroy':
                return False

        # Владельцы могут все
        if obj.owner == request.user:
            return True

        # Для просмотра разрешаем всем авторизованным
        if view.action == 'retrieve':
            return request.user.is_authenticated

        return False