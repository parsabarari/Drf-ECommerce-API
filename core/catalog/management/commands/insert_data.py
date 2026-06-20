import random
import uuid
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from accounts.models import Profile, User
from cart.models import CartItemModel, CartModel
from catalog.models import ProductCategoryModel, ProductModel, ProductStatusType
from orders.models import (
    CouponModel,
    OrderItemModel,
    OrderModel,
    OrderStatusType,
    UserAddressModel,
)
from payment.models import PaymentModel, PaymentStatusType
from reviews.models import ReviewModel, ReviewStatusType


CATEGORY_TITLES = [
    "Mobile",
    "Laptop",
    "Computer",
    "Graphic Card",
    "Accessories",
    "Gaming",
    "Storage",
]

PAYMENT_STATUSES = [
    PaymentStatusType.PENDING,
    PaymentStatusType.INITIATED,
    PaymentStatusType.SUCCESS,
    PaymentStatusType.FAILED,
]


class Command(BaseCommand):
    help = "Insert fake ecommerce data for catalog, carts, orders, reviews, and payments."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=8)
        parser.add_argument("--products", type=int, default=25)
        parser.add_argument("--orders", type=int, default=16)
        parser.add_argument("--reviews", type=int, default=35)
        parser.add_argument("--payments", type=int, default=12)
        parser.add_argument(
            "--password",
            type=str,
            default="a/@1234567",
            help="Password assigned to generated users.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["users"] < 1:
            raise CommandError("--users must be at least 1.")
        if options["products"] < 1:
            raise CommandError("--products must be at least 1.")

        users = self._create_users(options["users"], options["password"])
        categories = self._create_categories()
        products = self._create_products(options["products"], categories)
        coupons = self._create_coupons()

        self._create_carts(users, products)
        orders = self._create_orders(options["orders"], users, products, coupons)
        self._create_reviews(options["reviews"], users, products)
        payments = self._create_payments(options["payments"], orders)

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully inserted fake data: "
                f"{len(users)} users, {len(categories)} categories, "
                f"{len(products)} products, {len(orders)} orders, "
                f"{len(payments)} payments."
            )
        )

    def _create_users(self, count, password):
        users = []

        for index in range(count):
            user = User.objects.create_user(
                phone_number=self._unique_phone_number(index),
                password=password,
                email=self._unique_email(index),
                is_active=True,
                is_verified=random.choice([True, True, False]),
            )

            Profile.objects.filter(user=user).update(
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                description=self.fake.paragraph(nb_sentences=3),
            )
            users.append(user)

        return users

    def _create_categories(self):
        categories = []

        for title in CATEGORY_TITLES:
            category, _ = ProductCategoryModel.objects.get_or_create(
                slug=slugify(title),
                defaults={"title": title},
            )
            categories.append(category)

        return categories

    def _create_products(self, count, categories):
        products = []
        publish_index = random.randrange(count)

        for index in range(count):
            title = (
                f"{self.fake.unique.word().title()} "
                f"{self.fake.word().title()} {index + 1}"
            )
            price = Decimal(random.randint(120_000, 15_000_000))

            product = ProductModel.objects.create(
                title=title,
                slug=self._unique_slug(title, index),
                description=self.fake.paragraph(nb_sentences=8),
                category=random.choice(categories),
                price=price,
                discount_percent=random.choice([0, 0, 5, 10, 15, 20, 25]),
                stock=random.randint(3, 80),
                status=ProductStatusType.publish.value
                if index == publish_index
                else random.choice(
                    [
                        ProductStatusType.publish.value,
                        ProductStatusType.publish.value,
                        ProductStatusType.draft.value,
                    ]
                ),
            )
            products.append(product)

        return products

    def _create_coupons(self):
        coupons = []

        for index, discount in enumerate([10, 15, 20, 25], start=1):
            coupon, _ = CouponModel.objects.get_or_create(
                code=f"FAKE{discount}",
                defaults={
                    "discount_percent": discount,
                    "max_limit_usage": random.randint(20, 100),
                    "is_active": True,
                    "expiration_date": (
                        timezone.now() + timezone.timedelta(days=30 * index)
                    ),
                },
            )
            coupons.append(coupon)

        return coupons

    def _create_carts(self, users, products):
        published_products = [product for product in products if product.is_published]

        for user in users:
            cart, _ = CartModel.objects.get_or_create(user=user)

            for product in random.sample(
                published_products,
                k=min(3, len(published_products)),
            ):
                CartItemModel.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": random.randint(1, min(product.stock, 4))},
                )

    def _create_orders(self, count, users, products, coupons):
        orders = []
        published_products = [product for product in products if product.is_published]

        for _ in range(count):
            user = random.choice(users)
            address = self._create_address(user)
            coupon = random.choice(coupons + [None, None])
            order = OrderModel.objects.create(
                user=user,
                address=address.address,
                state=address.state,
                city=address.city,
                zip_code=address.zip_code,
                coupon=coupon,
                status=OrderStatusType.pending.value,
            )

            total_price = Decimal("0")
            selected_products = random.sample(
                published_products,
                k=random.randint(1, min(4, len(published_products))),
            )

            for product in selected_products:
                quantity = random.randint(1, min(product.stock, 3))
                item_price = product.final_price
                OrderItemModel.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=item_price,
                )
                total_price += item_price * quantity

            order.total_price = total_price
            order.save(update_fields=["total_price"])
            orders.append(order)

        return orders

    def _create_reviews(self, count, users, products):
        created_pairs = set()
        accepted_products = [product for product in products if product.is_published]

        for _ in range(count):
            user = random.choice(users)
            product = random.choice(accepted_products)
            pair = (user.id, product.id)

            if pair in created_pairs or ReviewModel.objects.filter(
                user=user,
                product=product,
            ).exists():
                continue

            ReviewModel.objects.create(
                user=user,
                product=product,
                description=self.fake.paragraph(nb_sentences=4),
                rate=random.randint(1, 5),
                status=random.choice(
                    [
                        ReviewStatusType.accepted.value,
                        ReviewStatusType.accepted.value,
                        ReviewStatusType.pending.value,
                    ]
                ),
            )
            created_pairs.add(pair)

    def _create_payments(self, count, orders):
        payments = []
        payable_orders = [order for order in orders if not hasattr(order, "payment")]

        for order in payable_orders[:count]:
            status = PAYMENT_STATUSES[len(payments) % len(PAYMENT_STATUSES)]
            ref_id = (
                str(random.randint(10_000_000, 99_999_999))
                if status == PaymentStatusType.SUCCESS
                else None
            )

            payment = PaymentModel.objects.create(
                user=order.user,
                order=order,
                amount=order.get_price(),
                authority=f"A{uuid.uuid4().hex}",
                ref_id=ref_id,
                status=status.value,
                gateway_response=self._gateway_response(status, ref_id),
            )

            if status == PaymentStatusType.SUCCESS:
                order.status = OrderStatusType.success.value
                order.save(update_fields=["status"])
            elif status == PaymentStatusType.FAILED:
                order.status = OrderStatusType.failed.value
                order.save(update_fields=["status"])

            payments.append(payment)

        return payments

    def _create_address(self, user):
        return UserAddressModel.objects.create(
            user=user,
            address=self.fake.street_address(),
            state=self.fake.state()[:50],
            city=self.fake.city()[:50],
            zip_code=self.fake.postcode()[:50],
        )

    def _gateway_response(self, status, ref_id):
        if status == PaymentStatusType.SUCCESS:
            return {"Status": 100, "RefID": ref_id, "message": "Fake successful payment"}
        if status == PaymentStatusType.FAILED:
            return {"Status": -22, "message": "Fake failed payment"}
        if status == PaymentStatusType.INITIATED:
            return {"Status": 100, "message": "Fake payment token created"}
        return {}

    def _unique_email(self, index):
        return f"fake-{uuid.uuid4().hex[:12]}-{index}@example.com"

    def _unique_phone_number(self, _index):
        while True:
            phone_number = f"09{random.randint(0, 999_999_999):09d}"
            if not User.objects.filter(phone_number=phone_number).exists():
                return phone_number

    def _unique_slug(self, title, index):
        return f"{slugify(title)}-{uuid.uuid4().hex[:8]}-{index}"
