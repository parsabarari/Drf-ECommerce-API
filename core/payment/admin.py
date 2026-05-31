from django.contrib import admin

from payment.models import PaymentModel


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "user",
        "order",
        "amount",
        "status",
        "authority",
        "ref_id",
        "created_date",
    ]

    list_filter = [
        "status",
        "created_date",
    ]

    search_fields = [
        "authority",
        "ref_id",
        "user__email",
        "order__id",
    ]

    ordering = [
        "-created_date",
    ]

    readonly_fields = [
        "authority",
        "ref_id",
        "gateway_response",
        "created_date",
        "updated_date",
    ]

    autocomplete_fields = [
        "user",
        "order",
    ]