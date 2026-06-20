import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError
from payment.models import PaymentModel, PaymentStatusType

class PaymentGatewayService:

    @staticmethod
    def create_payment(*, user, order):
        amount_toman = int(order.get_price())

        # ساختار نهایی و استاندارد هدرها و پی‌لود نسخه v4
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        
        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_toman,
            "description": f"بابت سفارش شماره {order.id}",
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
            "metadata": {"email": user.email}
        }

        try:
            response = requests.post(
                settings.ZARINPAL_REQUEST_URL, 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            res_data = response.json()
            
            # مدیریت خطای احتمالی لایه شبکه قبل از بررسی دیتا
            if response.status_code != 200:
                raise ValidationError({
                    "detail": "پاسخ نامعتبر از سرور زرین‌پال (Status Code Error)",
                    "gateway_response": res_data
                })

            # در نسخه v4، اگر کد ۱۰۰ باشد یعنی همه چیز عالی است و دیتا در رزولوشن "data" است
            data_body = res_data.get("data", {})
            errors_body = res_data.get("errors")

            if data_body and data_body.get("code") == 100:
                authority = data_body.get("authority")
                
                payment = PaymentModel.objects.create(
                    user=user,
                    order=order,
                    amount=order.get_price(),
                    authority=authority,
                    status=PaymentStatusType.PENDING,
                )

                # لینک واقعی درگاه سندباکس زرین‌پال
                payment_url = f"{settings.ZARINPAL_START_PAY_URL}{authority}"

                return {
                    "payment": payment,
                    "payment_url": payment_url,
                }
            
            raise ValidationError({
                "detail": "زرین‌پال درخواست را رد کرد.",
                "errors": errors_body
            })
            
        except requests.RequestException as e:
            raise ValidationError({"detail": f"خطای سخت‌افزاری/شبکه در اتصال به بانک: {e}"})