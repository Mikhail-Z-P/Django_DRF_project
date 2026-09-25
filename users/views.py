from rest_framework import viewsets
from .models import Payment
from .serializers import PaymentSerializer
from .filters import PaymentFilter


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.
    Поддерживает фильтрацию по курсу, уроку, способу оплаты и сортировку по дате.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]  # По умолчанию сортировка по убыванию даты
