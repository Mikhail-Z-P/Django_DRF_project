from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonCRUDTestCase(APITestCase):
    """Тесты CRUD-операций для уроков."""

    def setUp(self):
        """Создаёт пользователей, группу модераторов, курс и урок для тестов."""
        self.user = User.objects.create_user(
            email="user@test.com", password="TestPass123!"
        )
        self.moderator = User.objects.create_user(
            email="mod@test.com", password="TestPass123!"
        )
        self.moderator_group = Group.objects.create(name="moderators")
        self.moderator.groups.add(self.moderator_group)
        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

    def test_create_lesson_valid_link(self):
        """Проверка создания урока с корректной ссылкой на YouTube."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-list-create")
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=abc",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_invalid_link(self):
        """Проверка отказа при ссылке не на YouTube."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-list-create")
        data = {
            "title": "Плохой урок",
            "description": "Описание",
            "video_url": "https://google.com/video",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_lessons(self):
        """Проверка получения списка уроков авторизованным пользователем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_owner(self):
        """Проверка обновления урока владельцем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-retrieve-update-destroy", args=[self.lesson.id])
        data = {"title": "Обновлённый урок"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_moderator(self):
        """Проверка обновления урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-retrieve-update-destroy", args=[self.lesson.id])
        data = {"title": "Модератор изменил"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_owner(self):
        """Проверка удаления урока владельцем."""
        self.client.force_authenticate(user=self.user)
        url = reverse("lesson-retrieve-update-destroy", args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_lesson_moderator_forbidden(self):
        """Проверка запрета удаления урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-retrieve-update-destroy", args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_moderator_forbidden(self):
        """Проверка запрета создания урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        url = reverse("lesson-list-create")
        data = {
            "title": "Модератор пытается",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=test",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_create_forbidden(self):
        """Проверка запрета создания урока без авторизации."""
        url = reverse("lesson-list-create")
        data = {
            "title": "Без авторизации",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=test",
            "course": self.course.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubscriptionTestCase(APITestCase):
    """Тесты логики подписки на курс."""

    def setUp(self):
        """Создаёт пользователя и курс для тестов подписки."""
        self.user = User.objects.create_user(
            email="sub@test.com", password="TestPass123!"
        )
        self.course = Course.objects.create(
            title="Курс для подписки", description="Описание", owner=self.user
        )

    def test_create_subscription(self):
        """Проверка создания подписки."""
        self.client.force_authenticate(user=self.user)
        url = reverse("subscription-toggle")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_delete_subscription(self):
        """Проверка удаления подписки (toggle)."""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        url = reverse("subscription-toggle")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscription_unauthenticated(self):
        """Проверка отказа без авторизации."""
        url = reverse("subscription-toggle")
        data = {"course_id": self.course.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_is_subscribed_field(self):
        """Проверка поля is_subscribed в ответе курса."""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        url = reverse("course-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        course_data = next(
            (item for item in results if item["id"] == self.course.id), None
        )
        self.assertIsNotNone(course_data)
        self.assertTrue(course_data["is_subscribed"])
