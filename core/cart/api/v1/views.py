from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import MethodNotAllowed

from catalog.models import ProductModel, ProductStatusType
from ...models import CartModel, CartItemModel
from .serializers import CartSerializer, CartItemSerializer, CartSerializer
from ...services.cart import CartService



class CartViewSet(viewsets.ReadOnlyModelViewSet): # فقط خواندنی چون تغییرات از طریق CartItem gérer می‌شود
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        # کاربر فقط سبد خرید خودش را ببیند
        return CartModel.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def clear(self, request):

        cart = CartService.get_or_create_cart(
            request.user
        )

        CartService.clear_cart(cart)

        return Response(
            {"detail": "Cart cleared successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")



class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # آیتم‌های سبد خرید کاربر فعلی
        return CartItemModel.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):

        product_id = self.request.data.get("product_id")
        quantity = int(self.request.data.get("quantity", 1))

        CartService.add_item(
            user=self.request.user,
            product_id=product_id,
            quantity=quantity
        )

    def perform_update(self, serializer):

        quantity = int(self.request.data.get("quantity", 1))

        CartService.update_item(
            serializer.instance,
            quantity
        )

    def perform_destroy(self, instance):
        instance.delete()
        
    # اورراید کردن response ها برای اینکه همیشه کل سبد برگردد
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        cart = CartService.get_or_create_cart(request.user)
        cart_serializer = CartSerializer(cart) # استفاده از CartSerializer برای خروجی
        return Response(cart_serializer.data, status=status.HTTP_200_OK) # یا 201 اگر آیتم جدید اضافه شده

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        cart = CartService.get_or_create_cart(request.user)
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        cart = CartService.get_or_create_cart(request.user)
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


