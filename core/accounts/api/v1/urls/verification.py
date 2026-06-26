from django.urls import path
from ..views import RequestOTPView, VerifyOTPView


urlpatterns = [
    # otp
    path("request/", RequestOTPView.as_view(), name="otp_request"),
    path("verify/", VerifyOTPView.as_view(), name="otp_verify"),
]
