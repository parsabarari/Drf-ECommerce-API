from rest_framework import serializers
from ...models import ProductCategoryModel, ProductModel, ProductImageModel
from django.urls import reverse
from django.db.models import Avg



class CategorySerializer(serializers.ModelSerializer):
    relative_url = serializers.URLField(source='get_absolute_api_url',read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')

    class Meta:
        model = ProductCategoryModel
        fields = ['id', 'title', 'slug', 'relative_url', 'absolute_url']

    def get_abs_url(self,obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.slug) + '/'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = ['id', 'product', 'file', 'is_main', 'created_date']


class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'title',
            'slug',
            'price',
            'discount_percent',
            'stock',
            'average_rating',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):

    images = ProductImageSerializer(
        source='product_images',
        many=True,
        read_only=True
    )

    category = CategorySerializer(read_only=True)

    class Meta:
        model = ProductModel
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'category',
            'price',
            'discount_percent',
            'stock',
            'status',
            'average_rating',
            'created_date',
            'updated_date',
            'images',
        ]


class EmptySerializerClass(serializers.Serializer):
    pass


