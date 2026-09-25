from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
app_name = "users"

urlpatterns = router.urls
