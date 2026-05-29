from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError
from cart.models import CartModel
from orders.models import (
    OrderItemModel,
    OrderModel,
    OrderStatusType,
    UserAddressModel,
)
from orders.services.coupon import CouponService


class CheckoutService:

    @staticmethod
    @transaction.atomic
    def create_order(*, user, address_id, coupon_code=None):

        cart = (
            CartModel.objects
            .prefetch_related("cart_items__product")
            .filter(user=user)
            .first()
        )

        if not cart:
            raise ValidationError({
                "detail": "cart not found",
            })

        cart_items = cart.cart_items.all()

        if not cart_items.exists():
            raise ValidationError({
                "detail": "cart is empty",
            })

        address = (
            UserAddressModel.objects
            .filter(id=address_id, user=user)
            .first()
        )

        if not address:
            raise ValidationError({
                "address_id": "address not found",
            })

        coupon = None

        if coupon_code:
            coupon = CouponService.validate_coupon(
                user=user,
                coupon_code=coupon_code,
            )

        order = OrderModel.objects.create(
            user=user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            coupon=coupon,
            status=OrderStatusType.pending.value,
        )

        total_price = Decimal("0")

        order_items = []

        for cart_item in cart_items:

            product = cart_item.product

            if not product.is_published:
                raise ValidationError({
                    "detail": (
                        f"{product.title} is unavailable"
                    ),
                })

            if product.stock < cart_item.quantity:
                raise ValidationError({
                    "detail": (
                        f"{product.title} stock is insufficient"
                    ),
                })

            item_price = product.final_price

            order_item = OrderItemModel(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=item_price,
            )

            order_items.append(order_item)

            total_price += (
                item_price * cart_item.quantity
            )

        OrderItemModel.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save(update_fields=["total_price"])

        return order