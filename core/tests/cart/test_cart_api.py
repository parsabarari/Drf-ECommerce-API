import pytest

from cart.models import CartItemModel, CartModel
from tests.factories.cart import CartFactory, CartItemFactory
from tests.factories.catalog import ProductFactory


@pytest.mark.django_db
def test_authenticated_user_can_add_product_to_cart(auth_client, user):
    product = ProductFactory(price=50, stock=4)

    response = auth_client.post(
        "/cart/api/v1/cart-items/",
        {
            "product_id": product.id,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["total_price"] == 100
    assert response.data["cart_items"][0]["quantity"] == 2
    assert CartModel.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_user_cannot_update_another_users_cart_item(auth_client):
    cart_item = CartItemFactory()

    response = auth_client.patch(
        f"/cart/api/v1/cart-items/{cart_item.id}/",
        {"quantity": 3},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_clear_cart_empties_authenticated_users_cart(auth_client, user):
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart)

    response = auth_client.post(
        "/cart/api/v1/cart/clear/",
        format="json",
    )

    assert response.status_code == 204
    assert CartItemModel.objects.filter(cart=cart).count() == 0


@pytest.mark.django_db
def test_unauthenticated_user_cannot_view_cart(api_client):
    response = api_client.get("/cart/api/v1/cart/")

    assert response.status_code == 401
