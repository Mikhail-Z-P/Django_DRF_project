import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    """
    Набор фильтров для модели Payment.
    Позволяет фильтровать по курсу, уроку, способу оплаты и сортировать по дате.
    """

    class Meta:
        model = Payment
        fields = {
            "course": ["exact"],
            "lesson": ["exact"],
            "payment_method": ["exact"],
            "payment_date": ["gte", "lte"],
        }
