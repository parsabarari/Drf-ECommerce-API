from django.contrib import admin
from .models import ReviewModel



@admin.register(ReviewModel)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "product",
        "description",
        "rate",
        "status",
        "created_date",
    ]
    list_filter = ["user", "status", "product"]
    search_fields = ["description"]
    


