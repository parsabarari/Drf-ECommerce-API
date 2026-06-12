import pytest

from reviews.models import ReviewModel, ReviewStatusType
from tests.factories.catalog import ProductFactory
from tests.factories.user import UserFactory


@pytest.mark.django_db
def test_authenticated_user_can_create_review(auth_client, user):
    product = ProductFactory()

    response = auth_client.post(
        "/reviews/api/v1/reviews/",
        {
            "product": product.id,
            "rate": 4,
            "description": "Great product",
        },
        format="json",
    )

    review = ReviewModel.objects.get()

    assert response.status_code == 201
    assert review.user == user
    assert review.status == ReviewStatusType.pending.value


@pytest.mark.django_db
def test_user_cannot_review_same_product_twice(auth_client, user):
    product = ProductFactory()
    ReviewModel.objects.create(
        user=user,
        product=product,
        rate=5,
        description="First review",
    )

    response = auth_client.post(
        "/reviews/api/v1/reviews/",
        {
            "product": product.id,
            "rate": 4,
            "description": "Second review",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "already reviewed" in response.data["non_field_errors"][0]


@pytest.mark.django_db
def test_user_cannot_change_review_status(auth_client, user):
    product = ProductFactory()
    review = ReviewModel.objects.create(
        user=user,
        product=product,
        rate=3,
        description="Needs work",
    )

    response = auth_client.patch(
        f"/reviews/api/v1/reviews/{review.id}/",
        {"status": ReviewStatusType.accepted.value},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_edit_accepted_review(auth_client, user):
    product = ProductFactory()
    review = ReviewModel.objects.create(
        user=user,
        product=product,
        rate=5,
        description="Approved",
        status=ReviewStatusType.accepted.value,
    )

    response = auth_client.patch(
        f"/reviews/api/v1/reviews/{review.id}/",
        {"description": "Changed"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_access_another_users_review(auth_client):
    review = ReviewModel.objects.create(
        user=UserFactory(),
        product=ProductFactory(),
        rate=4,
        description="Private review",
    )

    response = auth_client.get(f"/reviews/api/v1/reviews/{review.id}/")

    assert response.status_code == 404
