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



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    relative_url = serializers.URLField(source='get_absolute_api_url',read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')

    class Meta:
        model = ProductModel
        fields = [
            'id', 'title', 'slug', 'description', 'category', 'price', 'discount_percent', 'stock', 'status', 'average_rating',
            'relative_url', 'absolute_url', 'created_date', 'updated_date', 'images',
        ]

    def get_abs_url(self,obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.slug) + '/'

    
    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        rep['state'] = 'list'
        if request.parser_context.get('kwargs').get('slug'):
            rep['state'] = 'single'
        
        rep['category'] = CategorySerializer(instance.category,context={'request':request}).data
        return rep
    



