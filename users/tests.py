from django.test import TestCase
from django.conf import settings


class SettingsTest(TestCase):
    """Проверка базовых настроек проекта."""

    def test_secret_key_exists(self):
        """Проверяет что SECRET_KEY задан."""
        self.assertTrue(hasattr(settings, "SECRET_KEY"))
        self.assertIsNotNone(settings.SECRET_KEY)

    def test_installed_apps(self):
        """Проверяет что необходимые приложения установлены."""
        required_apps = ["rest_framework", "users", "materials"]
        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
