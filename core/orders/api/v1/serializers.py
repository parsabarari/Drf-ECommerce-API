from rest_framework import serializers
from orders.models import (OrderModel,OrderItemModel,
                           UserAddressModel)
from catalog.api.v1.serializers import ProductListSerializer



class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItemModel

        fields = [
            "id",
            "product",
            "quantity",
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):

    order_items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    status = serializers.SerializerMethodField()

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderModel

        fields = [
            "id",

            "address",
            "state",
            "city",
            "zip_code",

            "total_price",
            "final_price",

            "status",

            "order_items",

            "created_date",
        ]

    def get_status(self, obj):

        return obj.get_status()

    def get_final_price(self, obj):

        return obj.get_price()
    

class CheckoutSerializer(serializers.Serializer):

    address_id = serializers.IntegerField()

    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True
    )


