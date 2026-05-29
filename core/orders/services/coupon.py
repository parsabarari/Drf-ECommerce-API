from django.utils import timezone
from rest_framework.exceptions import ValidationError
from orders.models import CouponModel



class CouponService:

    @staticmethod
    def validate_coupon(
        *,
        user,
        coupon_code,
    ):

        coupon = CouponModel.objects.filter(
            code=coupon_code,
            is_active=True,
        ).first()

        if not coupon:

            raise ValidationError({
                "coupon_code": "invalid coupon code"
            })

        if coupon.expiration_date:

            if coupon.expiration_date < timezone.now():

                raise ValidationError({
                    "coupon_code": "coupon expired"
                })

        if coupon.usage_count >= coupon.max_limit_usage:

            raise ValidationError({
                "coupon_code": "coupon usage limit exceeded"
            })

        if coupon.used_by.filter(id=user.id).exists():

            raise ValidationError({
                "coupon_code":
                "you already used this coupon"
            })

        return coupon

    @staticmethod
    def mark_coupon_as_used(
        *,
        coupon,
        user,
    ):

        coupon.used_by.add(user)

        coupon.usage_count += 1

        coupon.save(update_fields=["usage_count"])


