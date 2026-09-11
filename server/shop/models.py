import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    name = models.CharField(max_length=100)
    lang_prefix = models.CharField(max_length=100, default="en")

    class Meta:
        verbose_name_plural = "Languages"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="categories/", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Extra(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="extras/", null=True, blank=True)

    def __str__(self):
        return self.name


class Flavor(models.Model):
    name = models.CharField(max_length=100)
    extra_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="flavors/", null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    base_price = models.DecimalField(
        max_digits=6, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    available = models.BooleanField(default=True)
    offer = models.BooleanField(default=False)
    offer_precent = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    extras = models.ManyToManyField(Extra, blank=True, related_name="products")
    flavors = models.ManyToManyField(
        Flavor, blank=True, related_name="products")

    def __str__(self):
        return self.name


# ==========================================
# ORDER TABLES
# ==========================================


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", _("Pending Payment")),
        ("paid", _("Payment Received - In Queue")),
        ("preparing", _("Preparing")),
        ("completed", _("Ready for Pickup")),
        ("cancelled", _("Cancelled")),
    ]

    branch_id = models.IntegerField(default=1)
    daily_order_number = models.PositiveIntegerField(editable=False, null=True)
    reference_code = models.CharField(
        max_length=32, unique=True, editable=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price_base = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00)
    # Customer amounts (Selected currency, e.g., EUR)
    currency = models.CharField(
        max_length=5, default="USD"
    )  # e.g., 'EUR', 'PLN', 'RUB', 'TRY'
    exchange_rate = models.DecimalField(
        max_digits=10, decimal_places=4, default=1.0000
    )  # Rate used at the time of order
    total_price_customer = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00
    )

    def save(self, *args, **kwargs):
        # Generate reference code if not present
        if not self.reference_code:
            self.reference_code = f"ORD-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        if self.total_price_base:
            self.total_price_customer = self.total_price_base * self.exchange_rate

        # Generate daily order number resetting every midnight
        if not self.daily_order_number:
            today = timezone.now().date()
            todays_orders = Order.objects.filter(
                created_at__date=today, branch_id=self.branch_id
            )
            last_order = todays_orders.order_by("-daily_order_number").first()

            if last_order and last_order.daily_order_number:
                self.daily_order_number = last_order.daily_order_number + 1
            else:
                self.daily_order_number = 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.daily_order_number} ({self.reference_code})"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True
    )  # Keep record even if product is deleted
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2
    )  # Price of base product + extras per item
    total_price = models.DecimalField(
        max_digits=8, decimal_places=2
    )  # quantity * unit_price
    flavors = models.ManyToManyField(Flavor, blank=True)
    extras = models.ManyToManyField(Extra, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total price for this line item
        if self.unit_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name if self.product else 'Item'}"
