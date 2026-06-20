import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError
from cart.models import CartModel
from orders.models import OrderStatusType
from payment.models import PaymentModel, PaymentStatusType

class PaymentVerificationService:

    @staticmethod
    def verify_payment(*, authority, status_param=None):
        payment = (
            PaymentModel.objects
            .select_related("order", "user")
            .prefetch_related("order__order_items__product")
            .filter(authority=authority)
            .first()
        )

        if not payment:
            raise ValidationError({"detail": "payment not found"})

        # بررسی با املای حروف کوچک/بزرگ مدل شما
        if payment.status == PaymentStatusType.SUCCESS:
            return payment

        # اگر تراکنش از سمت کاربر یا بانک لغو شده باشد
        if status_param and status_param != "OK":
            payment.status = PaymentStatusType.FAILED
            payment.save(update_fields=["status"])
            
            order = payment.order
            order.status = OrderStatusType.failed  # تغییر به حروف کوچک
            order.save(update_fields=["status"])
            raise ValidationError({"detail": "Payment canceled by user."})

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": int(payment.amount),
            "authority": authority
        }

        try:
            response = requests.post(
                settings.ZARINPAL_VERIFY_URL, 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            res_data = response.json()
            
            data_body = res_data.get("data", {})
            errors_body = res_data.get("errors")

            if response.status_code == 200 and data_body:
                gateway_code = data_body.get("code")
                
                # ۱۰۰ = پرداخت موفق جدید، ۱۰۱ = قبلاً وریفای شده
                if gateway_code in [100, 101]:
                    ref_id = data_body.get("ref_id")
                    
                    # لاجیک بررسی موجودی انبار
                    order = payment.order
                    for item in order.order_items.all():
                        product = item.product
                        if product.stock < item.quantity:
                            payment.status = PaymentStatusType.FAILED
                            payment.save(update_fields=["status"])
                            
                            order.status = OrderStatusType.failed  # تغییر به حروف کوچک
                            order.save(update_fields=["status"])
                            raise ValidationError({"detail": f"{product.title} stock is insufficient"})

                        product.stock -= item.quantity
                        product.save(update_fields=["stock"])

                    # ذخیره وضعیت موفقیت تراکنش و سفارش
                    payment.status = PaymentStatusType.SUCCESS
                    payment.ref_id = str(ref_id)
                    payment.gateway_response = res_data
                    payment.save(update_fields=["status", "ref_id", "gateway_response"])

                    order.status = OrderStatusType.success  # تغییر به حروف کوچک
                    order.save(update_fields=["status"])

                    # پاکسازی سبد خرید
                    cart = CartModel.objects.filter(user=payment.user).first()
                    if cart:
                        cart.cart_items.all().delete()

                    return payment

            # در صورت عدم تایید بانک یا خطای زرین‌پال
            payment.status = PaymentStatusType.FAILED
            payment.gateway_response = res_data
            payment.save(update_fields=["status", "gateway_response"])
            
            order = payment.order
            order.status = OrderStatusType.failed  # تغییر به حروف کوچک
            order.save(update_fields=["status"])
            
            raise ValidationError({
                "detail": "تراکنش توسط سرور مرکزی زرین‌پال تایید نشد.",
                "errors": errors_body
            })

        except requests.RequestException as e:
            raise ValidationError({"detail": f"خطای شبکه در تایید تراکنش: {e}"})