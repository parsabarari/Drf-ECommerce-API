from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import (RegistrationSerializer, CustomAuthTokenSerializer,
                          CustomTokenObtainPairSerializer, ChangePasswordSerializer,
                          ProfileSerializer, ActivationResendSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import User, Profile
from django.shortcuts import get_object_or_404
from templated_email import send_templated_mail
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from jwt.exceptions import ExpiredSignatureError,InvalidSignatureError
import jwt
from django.contrib.auth import get_user_model
from rest_framework.throttling import ScopedRateThrottle

from .serializers import RequestOTPSerializer, VerifyOTPSerializer
from ...utils import OTPManager
from ...services import SmsService




class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            data = {
                'email':email
            }
            user_obj = get_object_or_404(User,email = email)
            token = self.get_tokens_for_user(user_obj)

            send_templated_mail(
                template_name='accounts/activation',
                context={'token':token},
                from_email='admin@admin.com',
                recipient_list=[email])
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    

class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
    

class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordApiView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = self.request.user
        return obj
    
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data = request.data)
        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({'details':'password changed successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj
    

class ActivationApiView(APIView):
    def get(self,request,token,*args,**kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except ExpiredSignatureError:
            return Response({'details':'token has been expired'},status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({'details':'token is not valid'},status=status.HTTP_400_BAD_REQUEST)
        user_obj = User.objects.get(pk=user_id)

        if user_obj.is_verified:
            return Response({'details':'account already activated'})
        user_obj.is_verified = True
        user_obj.save()
        return Response({'details':'your account have been verified and activated successfully'},status=status.HTTP_200_OK)
    
class ActivationResendApiView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self,request,*args,**kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data['user']
            token = self.get_tokens_for_user(user_obj)
            send_templated_mail(
                template_name='accounts/activation',
                context={'token':token},
                from_email='admin@admin.com',
                recipient_list=[user_obj.email])
            return Response({'details':'user activation resend successfully'},status=status.HTTP_200_OK)
        else:
            return Response({'details':'request failed'},status=status.HTTP_400_BAD_REQUEST)

    
    def get_tokens_for_user(self,user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


# otp

User = get_user_model()


class RequestOTPView(APIView):
    """اندپوینت درخواست کد OTP"""
    
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_request'

    serializer_class = RequestOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mobile = serializer.validated_data["mobile"]
        
        # تولید و ذخیره کد در Redis
        code = OTPManager.generate_code()
        OTPManager.store_otp(mobile, code)
        
        # ارسال پیامک
        sms_sent = SmsService.send_otp(mobile, code)
        print(f"======= TEST OTP CODE: {code} =======")
        if sms_sent:
            return Response({"detail": "کد تایید ارسال شد."}, status=status.HTTP_200_OK)
        
        # در پروداکشن برای راحتی دیباگ ترجیحا در محیط لوکال کد رو لاگ کنید، نه در ریسپانس
        return Response(
            {"detail": "خطا در ارسال پیامک. لطفا دوباره تلاش کنید."}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class VerifyOTPView(APIView):
    """اندپوینت تایید کد OTP"""
    serializer_class = VerifyOTPSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        mobile = serializer.validated_data["mobile"]
        code = serializer.validated_data["code"]
        
        # بررسی صحت کد
        if not OTPManager.verify_otp(mobile, code):
            return Response({"detail": "کد وارد شده اشتباه است یا منقضی شده."}, status=status.HTTP_400_BAD_REQUEST)
        
        # ساخت یا دریافت کاربر (فرض بر این است که USERNAME_FIELD شما mobile است یا فیلد متمایزی دارید)
        user, created = User.objects.get_or_create(phone_number=mobile, defaults={"is_active": True, "email": f"{mobile}@temporary.com"})
        
        # صدور توکن JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_new_user": created
        }, status=status.HTTP_200_OK)

