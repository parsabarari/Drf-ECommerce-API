import pytest
from rest_framework.exceptions import ValidationError

from cart.models import CartItemModel
from cart.services.cart import CartService
from catalog.models import ProductStatusType
from tests.factories.cart import CartFactory, CartItemFactory
from tests.factories.catalog import ProductFactory


@pytest.mark.django_db
def test_add_item_creates_cart_item(user):
    product = ProductFactory(price=100, stock=5)

    cart = CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=2,
    )

    cart_item = cart.cart_items.get(product=product)

    assert cart.user == user
    assert cart_item.quantity == 2
    assert cart.total_price == 200


@pytest.mark.django_db
def test_add_item_increases_existing_quantity(user):
    product = ProductFactory(stock=5)
    cart = CartFactory(user=user)
    CartItemFactory(cart=cart, product=product, quantity=2)

    CartService.add_item(
        user=user,
        product_id=product.id,
        quantity=3,
    )

    assert CartItemModel.objects.get(cart=cart, product=product).quantity == 5


@pytest.mark.django_db
def test_add_item_rejects_unpublished_product(user):
    product = ProductFactory(status=ProductStatusType.draft.value)

    with pytest.raises(ValidationError) as exc_info:
        CartService.add_item(
            user=user,
            product_id=product.id,
            quantity=1,
        )

    assert str(exc_info.value.detail["product"]) == "Product not found."


@pytest.mark.django_db
def test_update_item_deletes_when_quantity_is_zero():
    cart_item = CartItemFactory(quantity=2)

    CartService.update_item(
        cart_item=cart_item,
        quantity=0,
    )

    assert not CartItemModel.objects.filter(id=cart_item.id).exists()


@pytest.mark.django_db
def test_clear_cart_removes_all_items():
    cart = CartFactory()
    CartItemFactory(cart=cart)
    CartItemFactory(cart=cart, product=ProductFactory())

    CartService.clear_cart(cart)

    assert cart.cart_items.count() == 0
