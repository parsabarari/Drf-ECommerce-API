from rest_framework import serializers
from ...models import ReviewModel
from catalog.models import ProductModel
from django.conf import settings



class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username', read_only=True)

    class Meta:
        model = ReviewModel
        fields = [
            'id',
            'product',
            'user',
            'user_username',
            'rate',
            'description',
            'created_date',
            'updated_date',
            'status'
        ]
        read_only_fields = ['user', 'status', 'created_date', 'updated_date', 'user_username']

    def validate_product(self, value):
        if not value.is_published:
            raise serializers.ValidationError("the product is not available for review")
        return value

    def validate(self, data):
        user = self.context['request'].user
        product_id = self.instance.product.id if self.instance else self.initial_data.get('product')

        if not user.is_authenticated:
            raise serializers.ValidationError("user is not authenticated.")

        if product_id:
            if ReviewModel.objects.filter(user=user, product_id=product_id).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError("you've already reviewed this product, try for editing.")
        else:
             raise serializers.ValidationError("product field si required.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

