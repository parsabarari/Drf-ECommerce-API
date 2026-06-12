import pytest

from catalog.models import ProductStatusType
from orders.models import (
    OrderModel,
    OrderStatusType,
)
from tests.factories.cart import CartFactory, CartItemFactory
from tests.factories.catalog import ProductFactory
from tests.factories.orders import AddressFactory


@pytest.mark.django_db
def test_user_can_checkout(auth_client, user):

    product = ProductFactory(
        price=1000,
        stock=10,
    )

    cart = CartFactory(user=user)

    CartItemFactory(
        cart=cart,
        product=product,
        quantity=2,
    )

    address = AddressFactory(
        user=user,
    )

    response = auth_client.post(
        "/orders/api/v1/orders/checkout/",
        {"address_id": address.id},
        format="json",
    )

    assert response.status_code == 201

    order = OrderModel.objects.first()

    assert order is not None
    assert order.user == user
    assert order.status == OrderStatusType.pending.value
    assert order.total_price == 2000

    assert order.order_items.count() == 1



@pytest.mark.django_db
def test_checkout_with_empty_cart_returns_400(auth_client, user):

    AddressFactory(
        user=user,
    )

    response = auth_client.post(
        "/orders/api/v1/orders/checkout/",
        {"address_id": 1},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["detail"] == "cart not found"



@pytest.mark.django_db
def test_checkout_fails_when_stock_is_insufficient(auth_client, user):

    product = ProductFactory(
        price=1000,
        stock=1,
    )

    cart = CartFactory(user=user)

    CartItemFactory(
        cart=cart,
        product=product,
        quantity=5,
    )

    address = AddressFactory(
        user=user,
    )

    response = auth_client.post(
        "/orders/api/v1/orders/checkout/",
        {"address_id": address.id},
        format="json",
    )

    assert response.status_code == 400
    assert "stock is insufficient" in response.data["detail"]



@pytest.mark.django_db
def test_checkout_fails_for_unpublished_product(auth_client, user):

    product = ProductFactory(
        price=1000,
        stock=10,
        status=ProductStatusType.draft.value,
    )

    cart = CartFactory(user=user)

    CartItemFactory(
        cart=cart,
        product=product,
        quantity=1,
    )

    address = AddressFactory(
        user=user,
    )

    response = auth_client.post(
        "/orders/api/v1/orders/checkout/",
        {"address_id": address.id},
        format="json",
    )

    assert response.status_code == 400
    assert "unavailable" in response.data["detail"]
