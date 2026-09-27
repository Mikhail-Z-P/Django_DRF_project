from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserSerializer,
    UserRegistrationSerializer,
)
from .filters import PaymentFilter


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Расширяет стандартный сериализатор токенов, добавляя email в payload."""

    @classmethod
    def get_token(cls, user):
        """Добавляет поле email в токен."""
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        """Возвращает стандартный ответ с добавлением email."""
        data = super().validate(attrs)
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Эндпоинт для получения пары access и refresh токенов. Открыт для всех."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class UserRegistrationView(generics.CreateAPIView):
    """Эндпоинт для регистрации нового пользователя. Открыт для всех."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    """Эндпоинт для списка всех пользователей. Только для авторизованных."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Эндпоинт для получения, обновления и удаления пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.
    Поддерживает фильтрацию по курсу, уроку, способу оплаты и сортировку по дате.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
