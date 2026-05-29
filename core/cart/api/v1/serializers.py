from rest_framework import serializers
from ...models import CartItemModel, CartModel
from catalog.api.v1.serializers import ProductListSerializer 

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True) 
    total_item_price = serializers.ReadOnlyField()
    quantity = serializers.IntegerField(min_value=1, default=1)
 

    class Meta:
        model = CartItemModel
        fields = ['id', 'product', 'quantity', 'total_item_price']


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True) 
    
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartModel
        fields = ['id', 'user', 'cart_items', 'total_price', 'created_date', 'updated_date']
        read_only_fields = ['user', 'created_date', 'updated_date']


