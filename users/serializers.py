from rest_framework import serializers

from .models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Преобразует объекты платежей в JSON и обратно.
    """

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "course",
            "lesson",
            "amount",
            "payment_date",
            "payment_method",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра и редактирования пользователя."""

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "is_staff"]
        read_only_fields = ["is_staff"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя по email и паролю."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["email", "password", "phone", "city"]

    def create(self, validated_data):
        """Создаёт пользователя с хешированием пароля."""
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
