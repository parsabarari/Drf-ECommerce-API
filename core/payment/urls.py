from django.urls import (
    include,
    path,
)


urlpatterns = [
    path(
        "api/v1/",
        include("payment.api.v1.urls"),
    ),
]
