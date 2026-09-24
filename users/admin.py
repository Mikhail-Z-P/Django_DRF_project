from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель для кастомной модели пользователя."""
    list_display = ("email", "phone", "city", "is_staff")
