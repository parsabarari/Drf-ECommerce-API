from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

from orders.api.v1.serializers import (
    CheckoutSerializer,
    OrderSerializer,
)

from orders.models import OrderModel

from orders.services.checkout import CheckoutService


class OrderViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [permissions.IsAuthenticated]

    serializer_class = OrderSerializer

    def get_queryset(self):
        return (OrderModel.objects
            .select_related(
                "coupon",
                "user",
            )
            .prefetch_related(
                "order_items__product",
            )
            .filter(user=self.request.user)
        )

    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        order = CheckoutService.create_order(
            user=request.user,
            address_id=serializer.validated_data[
                "address_id"
            ],
            coupon_code=serializer.validated_data.get(
                "coupon_code"
            ),
        )

        response_serializer = OrderSerializer(
            order,
            context={
                "request": request,
            },
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_serializer_class(self):

        if self.action == "checkout":
            return CheckoutSerializer

        return OrderSerializer


