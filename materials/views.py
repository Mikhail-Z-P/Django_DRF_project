from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.permissions import IsNotModerator, IsOwner, IsOwnerOrModerator
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций над курсами с разделением прав."""

    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer

    def get_permissions(self):
        """Возвращает классы прав в зависимости от действия."""
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.IsAuthenticated(), IsNotModerator()]
        elif self.action in ["update", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwner(), IsNotModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Автоматически назначает текущего пользователя владельцем курса."""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Модераторы видят все курсы, остальные — только свои."""
        user = self.request.user
        if not user.is_authenticated:
            return Course.objects.none()
        if user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    @swagger_auto_schema(operation_summary="Список курсов")
    def list(self, request, *args, **kwargs):
        """Возвращает список курсов с пагинацией."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создание курса")
    def create(self, request, *args, **kwargs):
        """Создаёт новый курс. Только для не-модераторов."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Получение курса по ID")
    def retrieve(self, request, *args, **kwargs):
        """Возвращает детали конкретного курса."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление курса")
    def update(self, request, *args, **kwargs):
        """Полное обновление курса. Владелец или модератор."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление курса")
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление курса. Владелец или модератор."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удаление курса")
    def destroy(self, request, *args, **kwargs):
        """Удаление курса. Только владелец, не модератор."""
        return super().destroy(request, *args, **kwargs)


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-класс для списка уроков и создания нового урока."""

    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer

    def get_permissions(self):
        """Создание — только для не-модераторов, просмотр — для всех авторизованных."""
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsNotModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Автоматически назначает текущего пользователя владельцем урока."""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Модераторы видят все уроки, остальные — только свои."""
        user = self.request.user
        if not user.is_authenticated:
            return Lesson.objects.none()
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    @swagger_auto_schema(operation_summary="Список уроков")
    def get(self, request, *args, **kwargs):
        """Возвращает список уроков с пагинацией."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создание урока")
    def post(self, request, *args, **kwargs):
        """Создаёт новый урок с валидацией ссылки на YouTube."""
        return super().post(request, *args, **kwargs)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic-класс для получения, обновления и удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """Разделяет права по HTTP-методу."""
        if self.request.method in ["PUT", "PATCH"]:
            return [permissions.IsAuthenticated(), IsOwnerOrModerator()]
        elif self.request.method == "DELETE":
            return [permissions.IsAuthenticated(), IsOwner(), IsNotModerator()]
        return [permissions.IsAuthenticated()]

    @swagger_auto_schema(operation_summary="Получение урока по ID")
    def get(self, request, *args, **kwargs):
        """Возвращает детали конкретного урока."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление урока")
    def put(self, request, *args, **kwargs):
        """Полное обновление урока. Владелец или модератор."""
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление урока")
    def patch(self, request, *args, **kwargs):
        """Частичное обновление урока. Владелец или модератор."""
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удаление урока")
    def delete(self, request, *args, **kwargs):
        """Удаление урока. Только владелец, не модератор."""
        return super().delete(request, *args, **kwargs)


class SubscriptionView(APIView):
    """Эндпоинт для создания или удаления подписки на курс (toggle)."""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Переключение подписки на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID курса для подписки",
                )
            },
            required=["course_id"],
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            404: "Курс не найден",
        },
    )
    def post(self, request, *args, **kwargs):
        """Переключает подписку: если есть — удаляет, если нет — создаёт."""
        user = request.user
        course_id = request.data.get("course_id")
        course_item = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        return Response({"message": message})
