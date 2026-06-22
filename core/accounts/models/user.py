from django.db import models
from django.contrib.auth.models import (BaseUserManager,AbstractBaseUser,PermissionsMixin)
from ..validators import validate_iranian_cellphone_number


class UserManager(BaseUserManager):
    '''
    custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    '''
    def create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("phone number must be set")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, password, **extra_fields):
        '''
        create and save a SuperUser with the given email and password.
        '''
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_verified',True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must have is_superuser=True.')
        return self.create_user(phone_number,password,**extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    '''
    custom user model for our app
    '''
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=False, validators=[validate_iranian_cellphone_number])
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    email = models.EmailField(max_length=255,unique=True, null=True, blank=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()
    def __str__(self):
        return self.phone_number

