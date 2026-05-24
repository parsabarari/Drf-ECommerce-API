from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from catalog.models import ProductModel, ProductStatusType
from ...models import CartModel, CartItemModel
from .serializers import CartSerializer, CartItemSerializer, CartSerializer




class CartViewSet(viewsets.ReadOnlyModelViewSet): # فقط خواندنی چون تغییرات از طریق CartItem gérer می‌شود
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # کاربر فقط سبد خرید خودش را ببیند
        return CartModel.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_queryset().first()
        if cart:
            cart.cart_items.all().delete()
        return Response({"detail": "Cart cleared successfully."}, status=status.HTTP_204_NO_CONTENT)



class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # آیتم‌های سبد خرید کاربر فعلی
        return CartItemModel.objects.filter(cart__user=self.request.user)

    def get_cart(self):
        # گرفتن سبد خرید کاربر یا ساختن آن در صورت نبودن
        cart, created = CartModel.objects.get_or_create(user=self.request.user)
        return cart

    def perform_create(self, serializer):
        # هنگام اضافه کردن آیتم جدید
        product_id = self.request.data.get("product_id")
        quantity = self.request.data.get("quantity", 1)

        if not product_id:
            raise serializers.ValidationError({"product_id": "Product ID is required."})

        try:
            product = ProductModel.objects.get(id=product_id, status=ProductStatusType.publish.value)
        except ProductModel.DoesNotExist:
            raise serializers.ValidationError({"product": "Product not found or not published."})
        
        cart = self.get_cart()

        # بررسی اینکه آیا محصول از قبل در سبد هست یا نه
        cart_item, created = CartItemModel.objects.get_or_create(cart=cart, product_id=product_id)
        
        if created:
            cart_item.quantity = quantity
        else:
            # اگر محصول از قبل بود، تعداد را اضافه کن
            cart_item.quantity += quantity
        
        cart_item.save()
        # نیازی به serializing اینجا نیست، چون response از CartSerializer می‌آید
        # serializer.save() # این خط را حذف کن

    def perform_update(self, serializer):
        instance = serializer.instance
        quantity = int(self.request.data.get("quantity"))

        if quantity <= 0:
            instance.delete()
        else:
            instance.quantity = quantity
            instance.save()

    def perform_destroy(self, instance):
        instance.delete()
        
    # اورراید کردن response ها برای اینکه همیشه کل سبد برگردد
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        cart = self.get_cart()
        cart_serializer = CartSerializer(cart) # استفاده از CartSerializer برای خروجی
        return Response(cart_serializer.data, status=status.HTTP_200_OK) # یا 201 اگر آیتم جدید اضافه شده

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        cart = self.get_cart()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        
        cart = self.get_cart()
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


