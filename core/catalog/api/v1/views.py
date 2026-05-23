from rest_framework import viewsets, permissions
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ...models import ProductCategoryModel, ProductModel, ProductImageModel
from accounts.models import Profile
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer
from .pagination import DefaultPagination



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductCategoryModel.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        category = self.get_object()
        products = category.products.filter(is_active=True)  # یا product_set
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)



class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_date', 'category__title']
    pagination_class = DefaultPagination
    lookup_field = "slug"

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
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
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]



class ProductImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductImageModel.objects.all()
    serializer_class = ProductImageSerializer



