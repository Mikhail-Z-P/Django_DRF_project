from urllib.parse import urlparse

from rest_framework import serializers


class YoutubeLinkValidator:
    """Проверяет, что ссылка ведёт только на youtube.com."""

    def __init__(self, field):
        """Принимает имя поля, которое нужно валидировать."""
        self.field = field

    def __call__(self, value):
        """Разбирает URL и проверяет домен. Выбрасывает ошибку при несоответствии."""
        link = value.get(self.field) if isinstance(value, dict) else value
        if not link:
            return value
        parsed = urlparse(link)
        if "youtube.com" not in parsed.netloc:
            raise serializers.ValidationError(
                f"Поле '{self.field}' должно содержать ссылку только на youtube.com."
            )
        return value
