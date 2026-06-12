import factory

from accounts.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Sequence(
        lambda n: f"user{n}@example.com"
    )

    first_name = "Parsa"

    is_active = True

    password = factory.PostGenerationMethodCall(
        "set_password",
        "test1234"
    )