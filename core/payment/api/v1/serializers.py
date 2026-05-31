from rest_framework import serializers

from payment.models import (
    PaymentModel,
)


class PaymentSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = PaymentModel

        fields = [
            "id",
            "amount",
            "authority",
            "ref_id",
            "status",
            "gateway_response",
            "created_date",
        ]


class CreatePaymentSerializer(
    serializers.Serializer
):

    order_id = serializers.IntegerField()


class VerifyPaymentSerializer(
    serializers.Serializer
):

    authority = serializers.CharField()