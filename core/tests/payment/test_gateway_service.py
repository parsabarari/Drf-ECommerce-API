import pytest

from payment.models import PaymentModel, PaymentStatusType
from payment.services.gateway import PaymentGatewayService
from tests.factories.orders import OrderFactory


@pytest.mark.django_db
def test_create_payment_creates_pending_payment(user):
    order = OrderFactory(user=user, total_price=250)

    result = PaymentGatewayService.create_payment(
        user=user,
        order=order,
    )

    payment = PaymentModel.objects.get(order=order)

    assert result["payment"] == payment
    assert result["payment_url"] == f"/payment/mock/{payment.authority}/"
    assert payment.user == user
    assert payment.amount == 250
    assert payment.status == PaymentStatusType.pending.value
