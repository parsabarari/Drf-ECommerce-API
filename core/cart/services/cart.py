from rest_framework.exceptions import ValidationError

from cart.models import CartModel, CartItemModel
from catalog.models import ProductModel, ProductStatusType



class CartService:

    @staticmethod
    def get_or_create_cart(user):

        cart, _ = CartModel.objects.get_or_create(user=user)

        return cart

    @staticmethod
    def add_item(user, product_id, quantity):

        try:
            product = ProductModel.objects.get(
                id=product_id,
                status=ProductStatusType.publish.value
            )

        except ProductModel.DoesNotExist:
            raise ValidationError(
                {"product": "Product not found."}
            )

        if quantity > product.stock:
            raise ValidationError(
                {"quantity": "Insufficient stock."}
            )

        cart = CartService.get_or_create_cart(user)

        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            product=product
        )

        if created:
            cart_item.quantity = quantity

        else:

            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                raise ValidationError(
                    {"quantity": "Insufficient stock."}
                )

            cart_item.quantity = new_quantity

        cart_item.save()

        return cart

    @staticmethod
    def update_item(cart_item, quantity):

        if quantity <= 0:
            cart_item.delete()
            return

        if quantity > cart_item.product.stock:
            raise ValidationError(
                {"quantity": "Insufficient stock."}
            )

        cart_item.quantity = quantity
        cart_item.save()

    @staticmethod
    def clear_cart(cart):

        cart.cart_items.all().delete()


