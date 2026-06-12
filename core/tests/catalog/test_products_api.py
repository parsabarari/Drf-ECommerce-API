import pytest

from catalog.models import ProductModel, ProductStatusType, WishlistProductModel
from tests.factories.catalog import CategoryFactory, ProductFactory


@pytest.mark.django_db
def test_product_list_only_returns_published_products(api_client):
    published = ProductFactory(status=ProductStatusType.publish.value)
    ProductFactory(status=ProductStatusType.draft.value)

    response = api_client.get("/catalog/api/v1/products/")

    assert response.status_code == 200
    assert response.data["total_objects"] == 1
    assert response.data["results"][0]["slug"] == published.slug


@pytest.mark.django_db
def test_staff_can_see_draft_products(auth_client, user):
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    ProductFactory(status=ProductStatusType.publish.value)
    ProductFactory(status=ProductStatusType.draft.value)

    response = auth_client.get("/catalog/api/v1/products/")

    assert response.status_code == 200
    assert response.data["total_objects"] == 2


@pytest.mark.django_db
def test_category_products_returns_only_published_products(api_client):
    category = CategoryFactory(slug="phones")
    published = ProductFactory(category=category, status=ProductStatusType.publish.value)
    ProductFactory(category=category, status=ProductStatusType.draft.value)

    response = api_client.get(
        f"/catalog/api/v1/categories/{category.slug}/products/"
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.data] == [published.slug]


@pytest.mark.django_db
def test_authenticated_user_can_toggle_wishlist(auth_client, user):
    product = ProductFactory()

    add_response = auth_client.post(
        f"/catalog/api/v1/products/{product.slug}/toggle_wishlist/",
        format="json",
    )
    remove_response = auth_client.post(
        f"/catalog/api/v1/products/{product.slug}/toggle_wishlist/",
        format="json",
    )

    assert add_response.status_code == 201
    assert remove_response.status_code == 200
    assert not WishlistProductModel.objects.filter(
        user=user,
        product=product,
    ).exists()


@pytest.mark.django_db
def test_product_final_price_applies_discount():
    product = ProductFactory(price=100, discount_percent=25)

    assert product.final_price == 75
    assert product.is_discounted()
    assert ProductModel.objects.get(id=product.id).is_published
