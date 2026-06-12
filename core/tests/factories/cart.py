import factory

from cart.models import CartModel, CartItemModel
from tests.factories.catalog import ProductFactory


class CartFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CartModel

    user = factory.SubFactory(
        "tests.factories.user.UserFactory"
    )


class CartItemFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CartItemModel

    cart = factory.SubFactory(
        CartFactory
    )

    product = factory.SubFactory(
        ProductFactory
    )

    quantity = 1