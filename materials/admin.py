from django.contrib import admin

from materials.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Админ-панель для курсов."""

    list_display = ("title", "description")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Админ-панель для уроков."""

    list_display = ("title", "course", "video_url")
