import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from orders.services.coupon import CouponService
from tests.factories.orders import CouponFactory


@pytest.mark.django_db
def test_validate_coupon_returns_active_coupon(user):
    coupon = CouponFactory(code="SUMMER20")

    result = CouponService.validate_coupon(
        user=user,
        coupon_code="SUMMER20",
    )

    assert result == coupon


@pytest.mark.django_db
def test_validate_coupon_rejects_expired_coupon(user):
    CouponFactory(
        code="OLD20",
        expiration_date=timezone.now() - timezone.timedelta(days=1),
    )

    with pytest.raises(ValidationError) as exc_info:
        CouponService.validate_coupon(
            user=user,
            coupon_code="OLD20",
        )

    assert str(exc_info.value.detail["coupon_code"]) == "coupon expired"


@pytest.mark.django_db
def test_validate_coupon_rejects_coupon_used_by_user(user):
    coupon = CouponFactory(code="ONCE")
    coupon.used_by.add(user)

    with pytest.raises(ValidationError) as exc_info:
        CouponService.validate_coupon(
            user=user,
            coupon_code="ONCE",
        )

    assert str(exc_info.value.detail["coupon_code"]) == "you already used this coupon"


@pytest.mark.django_db
def test_mark_coupon_as_used_increments_usage_count(user):
    coupon = CouponFactory(usage_count=0)

    CouponService.mark_coupon_as_used(
        coupon=coupon,
        user=user,
    )

    coupon.refresh_from_db()

    assert coupon.usage_count == 1
    assert coupon.used_by.filter(id=user.id).exists()
