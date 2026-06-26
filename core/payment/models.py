from django.db import models
from django.conf import settings


class PaymentStatusType(models.IntegerChoices):
    PENDING = 1, "pending"
    INITIATED = 2, "initiated"
    SUCCESS = 3, "success"
    FAILED = 4, "failed"


class PaymentModel(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="payments")
    order = models.OneToOneField("orders.OrderModel", on_delete=models.PROTECT, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    authority = models.CharField(max_length=255, unique=True)
    ref_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(choices=PaymentStatusType.choices, default=PaymentStatusType.PENDING)
    gateway_response = models.JSONField(default=dict, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.user.email} - {self.order.id}"
    
