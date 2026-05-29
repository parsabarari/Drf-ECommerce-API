from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, ROUND_HALF_UP




class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")



class ProductCategoryModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title
        
    def get_absolute_api_url(self):
        return reverse("catalog:api-v1:category-detail", kwargs={"slug": self.slug})

    

class ProductModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        'ProductCategoryModel',
        on_delete=models.PROTECT,
        related_name='products'
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.IntegerField(default=0,validators = [MinValueValidator(0),MaxValueValidator(100)])
    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    
    average_rating = models.FloatField(default=0.0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_date"]

    def __str__(self):
        return self.title
    
    def get_absolute_api_url(self):
        return reverse("catalog:api-v1:product-detail", kwargs={"slug": self.slug})
    
    @property
    def final_price(self):
        discount_amount = (self.price * Decimal(self.discount_percent) / Decimal("100"))
        final_amount = self.price - discount_amount
        return final_amount.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    
    def is_discounted(self):
        return self.discount_percent != 0
    
    @property
    def is_published(self):
        return self.status == ProductStatusType.publish.value


class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="product_images")
    file = models.ImageField(upload_to='products/extra-img/')
    is_main = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main","-created_date"]



class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title

