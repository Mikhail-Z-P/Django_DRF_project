from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (CustomTokenObtainPairView, PaymentCreateView,
                    PaymentStatusView, PaymentViewSet, UserDetailView,
                    UserListView, UserRegistrationView)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
app_name = "users"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("payments/create/", PaymentCreateView.as_view(), name="payment-create"),
    path("payments/status/", PaymentStatusView.as_view(), name="payment-status"),
]

urlpatterns += router.urls
