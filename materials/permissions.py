from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, состоит ли пользователь в группе модераторов."""

    def has_permission(self, request, view):
        """Разрешает доступ только аутентифицированным модераторам."""
        return request.user.groups.filter(name="moderators").exists()


class IsNotModerator(permissions.BasePermission):
    """Проверяет, что пользователь НЕ является модератором."""

    def has_permission(self, request, view):
        """Разрешает доступ всем авторизованным, кто не в группе модераторов."""
        return not request.user.groups.filter(name="moderators").exists()


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        """Разрешает запись только владельцу объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """Разрешает доступ владельцам объекта или модераторам."""

    def has_object_permission(self, request, view, obj):
        """Проверяет права на изменение конкретного объекта."""
        if request.method in permissions.SAFE_METHODS:
            return True
        is_owner = obj.owner == request.user
        is_moderator = request.user.groups.filter(name="moderators").exists()
        return is_owner or is_moderator
