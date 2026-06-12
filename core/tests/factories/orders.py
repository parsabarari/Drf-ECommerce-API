import factory

from orders.models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    OrderStatusType,
    UserAddressModel,
)
from tests.factories.catalog import ProductFactory


class AddressFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserAddressModel

    user = factory.SubFactory(
        "tests.factories.user.UserFactory"
    )

    address = "Test Address"

    state = "Tehran"

    city = "Tehran"

    zip_code = "1234567890"


class CouponFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CouponModel

    code = factory.Sequence(
        lambda n: f"OFF{n}"
    )

    discount_percent = 20

    max_limit_usage = 10


class OrderFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = OrderModel

    user = factory.SubFactory(
        "tests.factories.user.UserFactory"
    )

    address = "Test Address"

    state = "Tehran"

    city = "Tehran"

    zip_code = "1234567890"

    total_price = 100

    status = OrderStatusType.pending.value


class OrderItemFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = OrderItemModel

    order = factory.SubFactory(
        OrderFactory
    )

    product = factory.SubFactory(
        ProductFactory
    )

    quantity = 1

    price = 100
