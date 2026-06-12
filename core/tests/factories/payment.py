import factory

from payment.models import PaymentModel, PaymentStatusType


class PaymentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = PaymentModel

    order = factory.SubFactory(
        "tests.factories.orders.OrderFactory"
    )

    user = factory.SelfAttribute("order.user")

    amount = factory.SelfAttribute("order.total_price")

    authority = factory.Sequence(
        lambda n: f"authority-{n}"
    )

    status = PaymentStatusType.pending.value
