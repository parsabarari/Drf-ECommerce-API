from rest_framework import viewsets
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Category, Product, ProductImage
from accounts.models import Profile
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from .pagination import DefaultPagination



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        category = self.get_object()
        products = category.products.filter(is_active=True)  # یا product_set
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_date', 'category__title']
    pagination_class = DefaultPagination
    lookup_field = "slug"

class ProductImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

