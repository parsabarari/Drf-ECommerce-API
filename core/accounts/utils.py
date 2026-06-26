import random
from django.core.cache import cache

class OTPManager:
    EXPIRY_TIME = 1000  # ۲ دقیقه انقضا به ثانیه

    @classmethod
    def generate_code(cls) -> str:
        return str(random.randint(10000, 99999))

    @classmethod
    def store_otp(cls, mobile: str, code: str) -> None:
        # کلید ذخیره‌سازی در ردیس برای جلوگیری از تداخل
        cache_key = f"otp:{mobile}"
        cache.set(cache_key, code, timeout=cls.EXPIRY_TIME)

    @classmethod
    def verify_otp(cls, mobile: str, user_code: str) -> bool:
        cache_key = f"otp:{mobile}"
        attempts_key = f"otp_attempts:{mobile}"
        
        stored_code = cache.get(cache_key)
        
        # اگر کدی تولید نشده یا منقضی شده باشد
        if not stored_code:
            return False
            
        # اگر کد درست بود
        if stored_code == user_code:
            cache.delete(cache_key)
            cache.delete(attempts_key)
            return True
            
        # اگر کد اشتباه بود
        # گرفتن تعداد تلاش‌های قبلی، اگر نبود مقدار پیش‌فرض 0 است
        attempts = cache.get(attempts_key, 0)
        attempts += 1
        
        if attempts >= 3:
            # کاربر ۳ بار یا بیشتر اشتباه کرده؛ کد اصلی و شمارنده هر دو پاک شوند
            cache.delete(cache_key)
            cache.delete(attempts_key)
        else:
            # ذخیره تعداد تلاش‌های جدید با همان زمان انقضا
            cache.set(attempts_key, attempts, timeout=cls.EXPIRY_TIME)
            
        return False
    