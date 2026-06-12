from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import OrderModel
from payment.api.v1.serializers import CreatePaymentSerializer, PaymentSerializer, VerifyPaymentSerializer
from payment.models import PaymentModel
from payment.services.gateway import PaymentGatewayService
from payment.services.verification import PaymentVerificationService


class PaymentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PaymentModel.objects.select_related("user", "order")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        serializer_map = {
            "create_payment": CreatePaymentSerializer,
            "verify_payment": VerifyPaymentSerializer,
        }
        return serializer_map.get(self.action, PaymentSerializer)

    @action(detail=False, methods=["post"], url_path="create")
    def create_payment(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = OrderModel.objects.filter(
            id=serializer.validated_data["order_id"],
            user=request.user,
        ).first()

        if not order:
            return Response({"detail": "order not found"}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(order, "payment"):
            return Response(PaymentSerializer(order.payment).data, status=status.HTTP_200_OK)

        result = PaymentGatewayService.create_payment(user=request.user, order=order)

        return Response(
            {"payment": PaymentSerializer(result["payment"]).data, "payment_url": result["payment_url"]},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="verify")
    def verify_payment(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentVerificationService.verify_payment(
            authority=serializer.validated_data["authority"],
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)