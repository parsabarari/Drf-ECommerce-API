from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from reviews.models import ReviewModel
from reviews.services.rating import update_product_rating


@receiver(post_save, sender=ReviewModel)
def review_saved(sender, instance, **kwargs):
    update_product_rating(instance.product)


@receiver(post_delete, sender=ReviewModel)
def review_deleted(sender, instance, **kwargs):
    update_product_rating(instance.product)