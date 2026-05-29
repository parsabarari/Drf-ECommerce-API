from django.db.models import Avg
from reviews.models import ReviewModel, ReviewStatusType


def update_product_rating(product):

    average_rating = (
        ReviewModel.objects.filter(
            product=product,
            status=ReviewStatusType.accepted.value
        ).aggregate(avg=Avg("rate"))["avg"]
    )

    product.average_rating = round(average_rating or 0, 1)
    product.save(update_fields=["average_rating"])