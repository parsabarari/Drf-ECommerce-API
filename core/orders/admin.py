from django.contrib import admin

from orders.models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    UserAddressModel,
)


class OrderItemInline(admin.TabularInline):

    model = OrderItemModel

    extra = 0

    can_delete = False

    readonly_fields = [
        "product",
        "quantity",
        "price",
        "created_date",
        "updated_date",
    ]


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "status",
        "total_price",
        "coupon",
        "created_date",
    ]

    list_filter = [
        "status",
        "created_date",
    ]

    search_fields = [
        "id",
        "user__email",
        "address",
        "city",
        "state",
    ]

    readonly_fields = [
        "total_price",
        "created_date",
        "updated_date",
    ]

    inlines = [OrderItemInline]

    ordering = ["-created_date"]


@admin.register(OrderItemModel)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "order",
        "product",
        "quantity",
        "price",
    ]

    search_fields = [
        "order__id",
        "product__title",
    ]

    readonly_fields = [
        "order",
        "product",
        "quantity",
        "price",
        "created_date",
        "updated_date",
    ]

    ordering = ["-created_date"]


@admin.register(CouponModel)
class CouponAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "code",
        "discount_percent",
        "usage_count",
        "max_limit_usage",
        "is_active",
        "expiration_date",
    ]

    list_filter = [
        "is_active",
        "created_date",
        "expiration_date",
    ]

    search_fields = [
        "code",
    ]

    filter_horizontal = [
        "used_by",
    ]

    readonly_fields = [
        "usage_count",
        "created_date",
        "updated_date",
    ]

    ordering = ["-created_date"]


@admin.register(UserAddressModel)
class UserAddressAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "state",
        "city",
        "zip_code",
        "created_date",
    ]

    list_filter = [
        "state",
        "city",
        "created_date",
    ]

    search_fields = [
        "user__email",
        "state",
        "city",
        "address",
        "zip_code",
    ]

    readonly_fields = [
        "created_date",
        "updated_date",
    ]

    ordering = ["-created_date"]


