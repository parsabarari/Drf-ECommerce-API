import pytest
from rest_framework.exceptions import ValidationError

from cart.models import CartItemModel
from payment.models import PaymentStatusType
from payment.services.verification import PaymentVerificationService
from orders.models import OrderStatusType
from tests.factories.cart import CartFactory, CartItemFactory
from tests.factories.catalog import ProductFactory
from tests.factories.orders import OrderFactory, OrderItemFactory
from tests.factories.payment import PaymentFactory


@pytest.mark.django_db
def test_verify_payment_marks_payment_and_order_success_and_decreases_stock():
    product = ProductFactory(stock=5, price=100)
    order = OrderFactory(total_price=200)
    OrderItemFactory(order=order, product=product, quantity=2, price=100)
    payment = PaymentFactory(order=order, user=order.user, amount=200)
    cart = CartFactory(user=order.user)
    CartItemFactory(cart=cart, product=product, quantity=2)

    result = PaymentVerificationService.verify_payment(
        authority=payment.authority,
    )

    payment.refresh_from_db()
    order.refresh_from_db()
    product.refresh_from_db()

    assert result == payment
    assert payment.status == PaymentStatusType.success.value
    assert payment.ref_id == f"REF-{payment.id}"
    assert payment.gateway_response == {"status": "success"}
    assert order.status == OrderStatusType.success.value
    assert product.stock == 3
    assert CartItemModel.objects.filter(cart=cart).count() == 0


@pytest.mark.django_db
def test_verify_payment_is_idempotent_for_successful_payment():
    payment = PaymentFactory(status=PaymentStatusType.success.value)

    result = PaymentVerificationService.verify_payment(
        authority=payment.authority,
    )

    assert result == payment


@pytest.mark.django_db
def test_verify_payment_fails_when_stock_is_insufficient():
    product = ProductFactory(stock=1)
    order = OrderFactory()
    OrderItemFactory(order=order, product=product, quantity=2)
    payment = PaymentFactory(order=order, user=order.user)

    with pytest.raises(ValidationError) as exc_info:
        PaymentVerificationService.verify_payment(
            authority=payment.authority,
        )

    payment.refresh_from_db()
    order.refresh_from_db()
    product.refresh_from_db()

    assert "stock is insufficient" in exc_info.value.detail["detail"]
    assert payment.status == PaymentStatusType.failed.value
    assert order.status == OrderStatusType.failed.value
    assert product.stock == 1


@pytest.mark.django_db
def test_verify_payment_rejects_unknown_authority():
    with pytest.raises(ValidationError) as exc_info:
        PaymentVerificationService.verify_payment(
            authority="missing",
        )

    assert str(exc_info.value.detail["detail"]) == "payment not found"
