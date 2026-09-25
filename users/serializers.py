from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Преобразует объекты платежей в JSON и обратно.
    """

    class Meta:
        model = Payment
        fields = ['id', 'user', 'course', 'lesson', 'amount', 'payment_date', 'payment_method']
