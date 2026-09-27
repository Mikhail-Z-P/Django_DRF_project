from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomTokenObtainPairView,
    PaymentViewSet,
    UserDetailView,
    UserListView,
    UserRegistrationView,
)

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
app_name = "users"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token-obtain"),
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]

urlpatterns += router.urls
