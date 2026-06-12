# tests/factories/catalog.py

import factory

from catalog.models import (
    ProductCategoryModel,
    ProductModel,
    ProductStatusType,
)


class CategoryFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ProductCategoryModel

    title = factory.Sequence(lambda n: f"Category {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")


class ProductFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ProductModel

    title = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")

    category = factory.SubFactory(CategoryFactory)

    price = 100
    stock = 10
    status = ProductStatusType.publish.value