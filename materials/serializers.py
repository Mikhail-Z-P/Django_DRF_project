from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Преобразует объекты урока в JSON и обратно.
    """
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'video_url', 'course']

class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Выводит количество уроков и список самих уроков.
    """
    total_lessons = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'total_lessons', 'lessons']

    def get_total_lessons(self, obj):
        """
        Метод для получения количества уроков.
        obj — экземпляр модели Course.
        Возвращает целое число — количество связанных уроков.
        """
        return obj.lessons.count()



