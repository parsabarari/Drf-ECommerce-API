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
    
    @action(detail=False, methods=["get"], url_path="verify-callback")
    def verify_callback(self, request):
        """
        اندpoint اختصاصی برای دریافت کاربر شوت شده از سمت بانک.
        زرین‌پال دیتا را به صورت متد GET به این روت می‌فرستد.
        """
        authority = request.query_params.get("Authority")
        status_param = request.query_params.get("Status")

        if not authority:
            return Response({"detail": "Authority token is missing"}, status=status.HTTP_400_BAD_REQUEST)

        # صدا زدن لایه سرویس با انتقال وضعیت ارسالی بانک
        payment = PaymentVerificationService.verify_payment(
            authority=authority,
            status_param=status_param
        )

        # پس از صحت پرداخت، می‌توانید کاربر را به یک صفحه لندینگ موفقیت‌آمیز در فرانت‌انداز ریدایرکت کنید
        # return redirect("https://my-frontend.com/payment/success")
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
