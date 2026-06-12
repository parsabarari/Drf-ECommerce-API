import pytest

from payment.models import PaymentModel
from tests.factories.orders import OrderFactory
from tests.factories.payment import PaymentFactory


@pytest.mark.django_db
def test_user_can_create_payment_for_own_order(auth_client, user):
    order = OrderFactory(user=user, total_price=300)

    response = auth_client.post(
        "/payment/api/v1/payments/create/",
        {"order_id": order.id},
        format="json",
    )

    payment = PaymentModel.objects.get(order=order)

    assert response.status_code == 201
    assert response.data["payment"]["id"] == payment.id
    assert response.data["payment_url"] == f"/payment/mock/{payment.authority}/"


@pytest.mark.django_db
def test_create_payment_returns_existing_payment(auth_client, user):
    order = OrderFactory(user=user)
    payment = PaymentFactory(order=order, user=user)

    response = auth_client.post(
        "/payment/api/v1/payments/create/",
        {"order_id": order.id},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["id"] == payment.id
    assert PaymentModel.objects.filter(order=order).count() == 1


@pytest.mark.django_db
def test_user_cannot_create_payment_for_another_users_order(auth_client):
    order = OrderFactory()

    response = auth_client.post(
        "/payment/api/v1/payments/create/",
        {"order_id": order.id},
        format="json",
    )

    assert response.status_code == 404
    assert response.data["detail"] == "order not found"


@pytest.mark.django_db
def test_user_only_lists_own_payments(auth_client, user):
    own_payment = PaymentFactory(order=OrderFactory(user=user), user=user)
    PaymentFactory()

    response = auth_client.get("/payment/api/v1/payments/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == own_payment.id
