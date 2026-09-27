from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.paginators import StandardResultsSetPagination
from materials.permissions import IsNotModerator, IsOwner, IsOwnerOrModerator
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций над курсами с разделением прав и пагинацией."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

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


class LessonListCreateView(generics.ListCreateAPIView):
    """Generic-класс для списка уроков и создания нового урока с пагинацией."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

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


class SubscriptionView(APIView):
    """Эндпоинт для создания или удаления подписки на курс (toggle)."""

    permission_classes = [permissions.IsAuthenticated]

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
