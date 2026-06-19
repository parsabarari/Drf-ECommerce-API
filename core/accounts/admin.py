from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('phone_number', 'is_superuser', 'is_active', 'is_verified')
    list_filter = ('phone_number', 'is_superuser', 'is_active', 'is_verified')
    searching_fields = ('phone_number',)
    ordering = ('phone_number',)
    fieldsets = (
        ('Authentication', {
            "fields": (
                'phone_number', 'email', 'password'
            ),
        }),
        ('permissions', {
            "fields": (
                'is_staff', 'is_active', 'is_superuser'
            ),
        }),
        ('group permissions', {
            "fields": (
                'groups', 'user_permissions'
            ),
        }),
        ('important date', {
            "fields": (
                'last_login',
            ),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'is_verified')
        }),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)