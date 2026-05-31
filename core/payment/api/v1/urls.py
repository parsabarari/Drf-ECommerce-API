from rest_framework.routers import DefaultRouter

from payment.api.v1.views import (
    PaymentViewSet,
)

app_name = "api-v1"

router = DefaultRouter()

router.register(
    "payments",
    PaymentViewSet,
    basename="payments",
)

urlpatterns = router.urls