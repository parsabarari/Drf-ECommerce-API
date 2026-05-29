from rest_framework.routers import DefaultRouter
from orders.api.v1.views import OrderViewSet



app_name = "api-v1"


router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = router.urls


