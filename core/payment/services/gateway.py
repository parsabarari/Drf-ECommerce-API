import uuid

from payment.models import (
    PaymentModel,
    PaymentStatusType,
)


class PaymentGatewayService:

    @staticmethod
    def create_payment(*, user, order):

        authority = uuid.uuid4().hex

        payment = PaymentModel.objects.create(
            user=user,
            order=order,
            amount=order.get_price(),
            authority=authority,
            status=PaymentStatusType.pending,
        )

        payment_url = (
            f"/payment/mock/{authority}/"
        )

        return {
            "payment": payment,
            "payment_url": payment_url,
        }