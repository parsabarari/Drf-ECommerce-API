from rest_framework import serializers
from ...models import Category, Product, ProductImage
from django.urls import reverse




class CategorySerializer(serializers.ModelSerializer):
    relative_url = serializers.URLField(source='get_absolute_api_url',read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'relative_url', 'absolute_url']

    def get_abs_url(self,obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.slug) + '/'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_main', 'created_date']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    relative_url = serializers.URLField(source='get_absolute_api_url',read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name='get_abs_url')

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'stock', 'is_active',
            'relative_url', 'absolute_url', 'category', 'created_date', 'updated_date', 'images'
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