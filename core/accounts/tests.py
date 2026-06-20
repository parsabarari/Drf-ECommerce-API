from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch

from .utils import OTPManager
from .services import SmsService


class OTPCoreLogicTestCase(TestCase):
    
    def setUp(self):
        # قبل از هر تست، حافظه کش را کاملاً پاک کن
        cache.clear()
        self.mobile = "09123456789"

    def test_otp_generation_and_storage(self):
        """تست اینکه کد به درستی تولید شده و در کش ذخیره می‌شود"""
        code = OTPManager.generate_code()
        
        # بررسی طول کد
        self.assertEqual(len(code), 5)
        self.assertTrue(code.isdigit())
        
        # ذخیره در کش
        OTPManager.store_otp(self.mobile, code)
        
        # بررسی اینکه کد مستقیماً در کش وجود دارد
        self.assertEqual(cache.get(f"otp:{self.mobile}"), code)

    def test_otp_verification_success(self):
        """تست تایید موفقیت‌آمیز کد و حذف آن از کش بعد از مصرف"""
        code = "55555"
        OTPManager.store_otp(self.mobile, code)
        
        # اقدام به وریفای با کد درست
        is_valid = OTPManager.verify_otp(self.mobile, code)
        
        self.assertTrue(is_valid)
        # کد یکبار مصرف است؛ باید بعد از تایید از کش حذف شده باشد
        self.assertIsNone(cache.get(f"otp:{self.mobile}"))

    def test_otp_verification_failed_and_brute_force_protection(self):
        """تست ورود کد اشتباه و مکانیسم قفل شدن بعد از ۳ بار تلاش اشتباه"""
        code = "11111"
        OTPManager.store_otp(self.mobile, code)
        
        # تلاش اول با کد اشتباه
        self.assertFalse(OTPManager.verify_otp(self.mobile, "99999"))
        
        # تلاش دوم با کد اشتباه
        self.assertFalse(OTPManager.verify_otp(self.mobile, "88888"))
        
        # تلاش سوم با کد اشتباه
        self.assertFalse(OTPManager.verify_otp(self.mobile, "77777"))
        
        # بعد از ۳ بار تلاش اشتباه، کد اصلی باید کلاً از کش پاک شده باشد
        self.assertIsNone(cache.get(f"otp:{self.mobile}"))

    @patch('requests.post')
    def test_sms_service_success(self, mock_post):
        """تست خروجی متد ارسال پیامک در صورت پاسخ موفقیت‌آمیز سرور sms.ir"""
        # شبیه‌سازی پاسخ موفقیت‌آمیز از سمت وب‌سرویس sms.ir
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": 1, "message": "Success"}
        
        result = SmsService.send_otp(self.mobile, "12345")
        self.assertTrue(result)
        
    @patch('requests.post')
    def test_sms_service_failure(self, mock_post):
        """تست خروجی متد ارسال پیامک در صورت خطای وب‌سرویس"""
        # شبیه‌سازی پاسخ خطای سرور
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"status": 0, "message": "Invalid API Key"}
        
        result = SmsService.send_otp(self.mobile, "12345")
        self.assertFalse(result)
