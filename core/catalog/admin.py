from django.contrib import admin
from .models import ProductCategoryModel, ProductModel, ProductImageModel, WishlistProductModel


class ProductImageInline(admin.TabularInline):
    model = ProductImageModel
    extra = 1


@admin.register(ProductCategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug"]
    prepopulated_fields = {
        "slug": ["title"]
    }


@admin.register(ProductModel)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "price",
        "stock",
        "status",
        "created_date",
    ]
    list_filter = ["category", "status", "created_date"]
    search_fields = ["title", "description"]
    prepopulated_fields = {
        "slug": ["title"]
    }
    inlines = [ProductImageInline]


@admin.register(ProductImageModel)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "is_main"]


@admin.register(WishlistProductModel)
class WishlistProductAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product"]


