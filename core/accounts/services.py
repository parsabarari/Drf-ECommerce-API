import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class SmsService:
    """سرویس ماژولار برای ارتباط با پنل sms.ir با استفاده از متد UltraFast"""
    
    API_URL = "https://api.sms.ir/v1/send/verify"

    @classmethod
    def send_otp(cls, mobile: str, code: str) -> bool:
        headers = {
            "X-API-KEY": settings.SMS_IR_API_KEY,
            "Accept": "text/plain",
            "Content-Type": "application/json",
        }
        payload = {
            "mobile": mobile,
            "templateId": settings.SMS_IR_TEMPLATE_ID,
            "parameters": [
<<<<<<< Updated upstream
                {"name": "Code", "value": str(code)}  # نام پارامتر باید با قالب sms.ir یکی باشد
=======
                {"name": "CODE", "value": str(code)}  # نام پارامتر باید با قالب sms.ir یکی باشد
>>>>>>> Stashed changes
            ]
        }
        
        try:
            response = requests.post(cls.API_URL, json=payload, headers=headers, timeout=5)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get("status") == 1:
                return True
            
            logger.error(f"SMS.ir error: {response_data}")
            return False
        except requests.RequestException as e:
            logger.error(f"Failed to connect to SMS.ir: {e}")
            return False