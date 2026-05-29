from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import ProductCategoryModel, ProductModel, ProductImageModel, WishlistProductModel, ProductStatusType
from accounts.models import Profile
from .serializers import (CategorySerializer, ProductListSerializer
                          , ProductDetailSerializer, ProductImageSerializer
                          , EmptySerializerClass)
from .pagination import DefaultPagination



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategoryModel.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        category = self.get_object()
        products = category.products.filter(status=ProductStatusType.publish.value)
        serializer = ProductListSerializer(products, many=True, context={"request": request})

        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductDetailSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_date', 'category__title']
    pagination_class = DefaultPagination
    lookup_field = "slug"

    @action(detail=True, methods=["post"])
    def toggle_wishlist(self, request, slug=None):
        product = self.get_object()
        user = request.user
        
        # بررسی وجود محصول در لیست علاقه‌مندی‌ها
        wishlist_item = WishlistProductModel.objects.filter(user=user, product=product)
        
        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({"message": "از لیست علاقه‌مندی‌ها حذف شد."}, status=status.HTTP_200_OK)
        else:
            WishlistProductModel.objects.create(user=user, product=product)
            return Response({"message": "به لیست علاقه‌مندی‌ها اضافه شد."}, status=status.HTTP_201_CREATED)
        
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]

        elif self.action == 'toggle_wishlist':
            permission_classes = [permissions.IsAuthenticated]

        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):

        if self.action == 'list':
            return ProductListSerializer
        
        if self.action == 'toggle_wishlist':
            return EmptySerializerClass

        return ProductDetailSerializer
    
    def get_queryset(self):
        queryset = ProductModel.objects.select_related("category").prefetch_related("product_images")
        if self.request.user.is_staff:
            return queryset
        
        return queryset.filter(status=ProductStatusType.publish.value)


