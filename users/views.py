from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import PaymentFilter
from .models import Payment, User
from .serializers import (PaymentSerializer, UserRegistrationSerializer,
                          UserSerializer)
from .services import (create_checkout_session, create_price, create_product,
                       retrieve_session)


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

    @swagger_auto_schema(operation_summary="Получение JWT-токенов")
    def post(self, request, *args, **kwargs):
        """Возвращает access и refresh токены по email и паролю."""
        return super().post(request, *args, **kwargs)


class UserRegistrationView(generics.CreateAPIView):
    """Эндпоинт для регистрации нового пользователя. Открыт для всех."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(operation_summary="Регистрация пользователя")
    def post(self, request, *args, **kwargs):
        """Создаёт нового пользователя по email и паролю."""
        return super().post(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    """Эндпоинт для списка всех пользователей. Только для авторизованных."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Список пользователей")
    def get(self, request, *args, **kwargs):
        """Возвращает список всех пользователей."""
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Эндпоинт для получения, обновления и удаления пользователя."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение пользователя по ID")
    def get(self, request, *args, **kwargs):
        """Возвращает данные конкретного пользователя."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление пользователя")
    def put(self, request, *args, **kwargs):
        """Полное обновление данных пользователя."""
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление пользователя")
    def patch(self, request, *args, **kwargs):
        """Частичное обновление данных пользователя."""
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удаление пользователя")
    def delete(self, request, *args, **kwargs):
        """Удаляет пользователя."""
        return super().delete(request, *args, **kwargs)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления платежами с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    @swagger_auto_schema(operation_summary="Список платежей")
    def list(self, request, *args, **kwargs):
        """Возвращает список платежей с пагинацией."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создание платежа вручную")
    def create(self, request, *args, **kwargs):
        """Создаёт платёж без Stripe (для записи наличных оплат)."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Получение платежа по ID")
    def retrieve(self, request, *args, **kwargs):
        """Возвращает детали конкретного платежа."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление платежа")
    def update(self, request, *args, **kwargs):
        """Полное обновление данных платежа."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление платежа")
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление данных платежа."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удаление платежа")
    def destroy(self, request, *args, **kwargs):
        """Удаляет запись о платеже."""
        return super().destroy(request, *args, **kwargs)


class PaymentCreateView(generics.CreateAPIView):
    """Создание платежа с интеграцией Stripe."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создание платежа за курс через Stripe",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "course": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID курса для оплаты",
                ),
                "amount": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Сумма оплаты в рублях",
                ),
                "payment_method": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Способ оплаты: cash или transfer",
                ),
            },
            required=["course", "amount", "payment_method"],
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "payment": openapi.Schema(type=openapi.TYPE_OBJECT),
                    "payment_url": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            400: "Ошибка в данных запроса",
        },
    )
    def create(self, request, *args, **kwargs):
        """Создаёт продукт, цену и сессию в Stripe, сохраняет ссылку на оплату."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data.get("course")
        amount = serializer.validated_data["amount"]

        product_id = create_product(
            name=f"Курс: {course.title}" if course else "Оплата",
            description=course.description if course else "",
        )
        price_id = create_price(product_id, int(amount * 100))
        session_data = create_checkout_session(
            price_id,
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )

        payment = serializer.save(
            user=request.user,
            stripe_product_id=product_id,
            stripe_price_id=price_id,
            stripe_session_id=session_data["session_id"],
            payment_link=session_data["payment_url"],
        )

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "payment_url": session_data["payment_url"],
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusView(APIView):
    """Проверка статуса платежа через Stripe."""

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Проверка статуса платежа",
        manual_parameters=[
            openapi.Parameter(
                "session_id",
                openapi.IN_QUERY,
                description="ID сессии Stripe",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: "Статус платежа получен"},
    )
    def get(self, request, *args, **kwargs):
        """Возвращает статус платёжной сессии из Stripe по session_id."""
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "Не передан session_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            session_data = retrieve_session(session_id)
            return Response(session_data)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
