from rest_framework.exceptions import ValidationError

from cart.models import CartModel

from orders.models import (
    OrderStatusType,
)

from payment.models import (
    PaymentModel,
    PaymentStatusType,
)


class PaymentVerificationService:

    @staticmethod
    def verify_payment(*, authority):

        payment = (
            PaymentModel.objects
            .select_related(
                "order",
                "user",
            )
            .prefetch_related(
                "order__order_items__product",
            )
            .filter(
                authority=authority,
            )
            .first()
        )

        if not payment:

            raise ValidationError({
                "detail": "payment not found",
            })

        if (
            payment.status
            == PaymentStatusType.success
        ):

            return payment

        order = payment.order

        for item in order.order_items.all():

            product = item.product

            if product.stock < item.quantity:

                payment.status = (
                    PaymentStatusType.failed
                )

                payment.save(
                    update_fields=["status"]
                )

                order.status = (
                    OrderStatusType.failed
                )

                order.save(
                    update_fields=["status"]
                )

                raise ValidationError({
                    "detail": (
                        f"{product.title} "
                        "stock is insufficient"
                    ),
                })

            product.stock -= item.quantity

            product.save(
                update_fields=["stock"]
            )

        payment.status = (
            PaymentStatusType.success
        )

        payment.ref_id = (
            f"REF-{payment.id}"
        )

        payment.gateway_response = {
            "status": "success",
        }

        payment.save(
            update_fields=[
                "status",
                "ref_id",
                "gateway_response",
            ]
        )

        order.status = (
            OrderStatusType.success
        )

        order.save(
            update_fields=["status"]
        )

        cart = (
            CartModel.objects
            .filter(user=payment.user)
            .first()
        )

        if cart:

            cart.cart_items.all().delete()

        return payment
