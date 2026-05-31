from django.db import models


class PaymentStatusType(models.IntegerChoices):
    pending = 1, "pending"
    success = 2, "success"
    failed = 3, "failed"


class PaymentModel(models.Model):

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    order = models.OneToOneField(
        "orders.OrderModel",
        on_delete=models.PROTECT,
        related_name="payment",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    authority = models.CharField(
        max_length=255,
        unique=True,
    )

    ref_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    status = models.IntegerField(
        choices=PaymentStatusType.choices,
        default=PaymentStatusType.pending,
    )

    gateway_response = models.JSONField(
        default=dict,
        blank=True,
    )

    created_date = models.DateTimeField(
        auto_now_add=True,
    )

    updated_date = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):

        return (
            f"{self.user.email} - "
            f"{self.order.id}"
        )