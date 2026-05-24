from django.contrib import admin
from .models import CartModel, CartItemModel


@admin.register(CartModel)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "created_date",
        "updated_date",
        "total_price",
    ]

@admin.register(CartItemModel)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "cart",
        "product",
        "quantity",
        "created_date",
        "updated_date",
        "total_item_price",
    ]
    list_filter = ["cart", "product"]

    