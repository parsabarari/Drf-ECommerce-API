from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator




class ReviewStatusType(models.IntegerChoices):
    pending = 1, "در انتظار تایید"
    accepted = 2, "تایید شده"
    rejected = 3, "رد شده"


class ReviewModel(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    product = models.ForeignKey('catalog.ProductModel',on_delete=models.CASCADE, related_name='reviews')
    description = models.TextField()
    rate = models.IntegerField(default=1, validators=[
                               MinValueValidator(1), MaxValueValidator(5)])
    status = models.IntegerField(
        choices=ReviewStatusType.choices, default=ReviewStatusType.pending.value)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        unique_together = ('user', 'product')
    
    def __str__(self):
        return f"{self.user} - {self.product.id}"
    
    
    def get_status(self):
        return {
            "id":self.status,
            "title":ReviewStatusType(self.status).name,
            "label":ReviewStatusType(self.status).label,
        }


