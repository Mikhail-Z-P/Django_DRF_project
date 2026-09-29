from rest_framework import serializers

from .models import Course, Lesson
from .validators import YoutubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор уроков с валидацией ссылок на YouTube."""

    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "video_url", "course", "owner"]
        read_only_fields = ["owner"]
        validators = [YoutubeLinkValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курсов с подсчётом уроков и признаком подписки."""

    total_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "total_lessons",
            "lessons",
            "owner",
            "is_subscribed",
        ]
        read_only_fields = ["owner"]

    def get_total_lessons(self, obj):
        """Возвращает количество уроков в курсе."""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли текущий пользователь на курс."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscribers.filter(user=request.user).exists()
