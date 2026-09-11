from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import Category
from .models import Extra, Flavor, Product, OrderItem, Order


class FlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ["id", "name", "extra_price", "available", "image"]


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = ["id", "name", "price", "available", "image"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "base_price",
            "available",
            "offer",
            "offer_precent",
            "image",
            "category",
        ]


# Used specifically for returning a product along with its available options
class ProductWithOptionsSerializer(serializers.ModelSerializer):
    flavors = FlavorSerializer(many=True, read_only=True)
    extras = ExtraSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "base_price",
            "image",
            "flavors",
            "extras",
        ]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = Category
        fields = ["id", "name", "image"]


class OrderItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    flavor_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )
    extra_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )


class OrderCreateSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField(default=1)
    currency = serializers.CharField(max_length=5, required=False, default="USD")
    exchange_rate = serializers.FloatField(required=False, default=1.0)
    items = OrderItemCreateSerializer(many=True, allow_empty=False)

    def validate_exchange_rate(self, value):
        """Converts float/decimal to Decimal and rounds to 4 decimal places."""
        try:
            rate = Decimal(str(value)).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
            return rate
        except Exception:
            raise serializers.ValidationError("Invalid exchange rate format.")

    @transaction.atomic
    def create(self, validated_data):
        # 1. Pop items once from validated_data
        items_data = validated_data.pop("items", [])
        branch_id = validated_data.get("branch_id", 1)
        currency = validated_data.get("currency", "USD")
        exchange_rate = validated_data.get("exchange_rate", Decimal("1.0000"))

        # 2. Create the base Order instance
        order = Order.objects.create(
            branch_id=branch_id,
            currency=currency,
            exchange_rate=exchange_rate,
            status="pending",
        )

        order_total_base = Decimal("0.00")

        # 3. Process each line item
        for item_data in items_data:
            product = Product.objects.get(id=item_data["product_id"])
            quantity = item_data.get("quantity", 1)

            flavors = Flavor.objects.filter(id__in=item_data.get("flavor_ids", []))
            extras = Extra.objects.filter(id__in=item_data.get("extra_ids", []))

            # Calculate unit_price: product base_price + flavor extras + topping extras
            unit_price = product.base_price
            for flavor in flavors:
                unit_price += flavor.extra_price
            for extra in extras:
                unit_price += extra.price

            # Create OrderItem instance
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
            )

            # Associate ManyToMany relations
            order_item.flavors.set(flavors)
            order_item.extras.set(extras)

            # Calculate line total and accumulate base total
            item_line_total = unit_price * quantity
            order_item.total_price = item_line_total
            order_item.save()

            order_total_base += item_line_total

        # 4. Set total_price_base (Order.save handles total_price_customer calculation)
        order.total_price_base = order_total_base
        order.save()

        return order


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True, default="Item Unavailable"
    )
    item_total_price = serializers.DecimalField(
        source="total_price", max_digits=8, decimal_places=2, read_only=True
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "unit_price",
            "quantity",
            "item_total_price",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.product and obj.product.image:
            if request is not None:
                return request.build_absolute_uri(obj.product.image.url)
            return obj.product.image.url
        return None


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M:%S")
    order_id = serializers.IntegerField(source="id")
    customer_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id",
            "daily_order_number",
            "reference_code",
            "total_price_base",
            "total_price_customer",
            "currency",
            "date",
            "customer_status",
            "items",
        ]

    def get_customer_status(self, obj):
        # Using _() translates the string dynamically based on Accept-Language
        status_mapping = {
            "pending": _("Awaiting Counter Payment"),
            "paid": _("Paid — In Queue"),
            "preparing": _("Being Prepared"),
            "completed": _("Ready for Pickup"),
            "cancelled": _("Cancelled"),
        }
        translated_status = status_mapping.get(obj.status, obj.status)
        return str(translated_status)  # Force evaluation into string for JSON


class OrderSummarySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M:%S")
    order_id = serializers.IntegerField(source="id")
    customer_status = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id",
            "daily_order_number",
            "reference_code",
            "date",
            "customer_status",
            "total_price_base",
            "image",
        ]

    def get_customer_status(self, obj):
        status_mapping = {
            "pending": _("Awaiting Counter Payment"),
            "paid": _("Paid — In Queue"),
            "preparing": _("Being Prepared"),
            "completed": _("Ready for Pickup"),
            "cancelled": _("Cancelled"),
        }
        return status_mapping.get(obj.status, obj.status)

    def get_image(self, obj):
        # Find the first item in the order that has a product with an image attached
        request = self.context.get("request")
        for item in obj.items.all():
            if item.product and item.product.image:
                if request:
                    return request.build_absolute_uri(item.product.image.url)
                return item.product.image.url
        return None  # Returns null if no product image exists in this order


class StaffFlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavor
        fields = ["id", "name"]


class StaffExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = ["id", "name"]


class StaffOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    flavors = StaffFlavorSerializer(many=True, read_only=True)
    extras = StaffExtraSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_image",
            "quantity",
            "unit_price",
            "total_price",
            "flavors",
            "extras",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request")
        if obj.product and getattr(obj.product, "image", None):
            return (
                request.build_absolute_uri(obj.product.image.url)
                if request
                else obj.product.image.url
            )
        return None

    def get_product_name(self, obj):
        return obj.product.name if obj.product else "Deleted Product"


class StaffOrderDashboardSerializer(serializers.ModelSerializer):
    items = StaffOrderItemSerializer(many=True, read_only=True)
    created_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "daily_order_number",
            "reference_code",
            "status",
            "currency",
            "total_price_customer",
            "created_time",
            "items",
        ]

    def get_created_time(self, obj):
        return obj.created_at.strftime("%I:%M:%S %p")
