from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# =========================================================
# CATEGORY
# =========================================================

class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        max_length=120,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220,
        unique=True
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0)
        ]
    )

    image = models.ImageField(
        upload_to="products/"
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    reviews_count = models.PositiveIntegerField(
        default=0
    )

    is_featured = models.BooleanField(
        default=False
    )

    is_new_arrival = models.BooleanField(
        default=False
    )

    is_bestseller = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["is_active"]
            ),
            models.Index(
                fields=["category", "is_active"]
            ),
            models.Index(
                fields=["brand"]
            ),
            models.Index(
                fields=["-created_at"]
            ),
        ]

    def __str__(self):
        return self.name

    # -----------------------------------------------------
    # FINAL PRICE
    # -----------------------------------------------------

    @property
    def final_price(self):

        if (
            self.sale_price is not None
            and self.sale_price < self.price
        ):
            return self.sale_price

        return self.price

    # -----------------------------------------------------
    # DISCOUNT
    # -----------------------------------------------------

    @property
    def discount_percentage(self):

        if (
            self.sale_price is not None
            and self.price > 0
            and self.sale_price < self.price
        ):

            discount = (
                (self.price - self.sale_price)
                / self.price
            ) * 100

            return round(discount)

        return 0

    # -----------------------------------------------------
    # STOCK
    # -----------------------------------------------------

    @property
    def in_stock(self):
        return self.stock > 0

    # -----------------------------------------------------
    # STOCK STATUS
    # -----------------------------------------------------

    @property
    def stock_status(self):

        if self.stock <= 0:
            return "Out of Stock"

        if self.stock <= 5:
            return "Only Few Left"

        return "In Stock"


# =========================================================
# WISHLIST
# =========================================================

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "product"
                ],
                name="unique_user_product_wishlist"
            )
        ]

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
        ]

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.product.name}"
        )


# =========================================================
# CART
# =========================================================

class Cart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.user.username}'s Cart"
        )

    # -----------------------------------------------------
    # TOTAL ITEMS
    # -----------------------------------------------------

    @property
    def total_items(self):

        return sum(
            item.quantity
            for item in self.items.all()
        )

    # -----------------------------------------------------
    # SUBTOTAL
    # -----------------------------------------------------

    @property
    def subtotal(self):

        return sum(
            item.total_price
            for item in self.items.all()
        )

    # -----------------------------------------------------
    # SHIPPING
    # -----------------------------------------------------

    @property
    def shipping_charge(self):

        if self.subtotal >= 499:
            return 0

        return 49

    # -----------------------------------------------------
    # GRAND TOTAL
    # -----------------------------------------------------

    @property
    def total_amount(self):

        return (
            self.subtotal +
            self.shipping_charge
        )


# =========================================================
# CART ITEM
# =========================================================

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ]
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "cart",
                    "product"
                ],
                name="unique_cart_product"
            )
        ]

        ordering = ["-added_at"]

    def __str__(self):

        return (
            f"{self.product.name} "
            f"x {self.quantity}"
        )

    # -----------------------------------------------------
    # ITEM TOTAL
    # -----------------------------------------------------

    @property
    def total_price(self):

        return (
            self.product.final_price *
            self.quantity
        )


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):

    STATUS_CHOICES = [

        ("pending", "Pending"),

        ("confirmed", "Confirmed"),

        ("shipped", "Shipped"),

        ("delivered", "Delivered"),

        ("cancelled", "Cancelled"),

    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True
    )

    full_name = models.CharField(
        max_length=150
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
            models.Index(
                fields=["status"]
            ),
        ]

    def __str__(self):

        return self.order_number

    # -----------------------------------------------------
    # STATUS LABEL
    # -----------------------------------------------------

    @property
    def status_label(self):

        return self.get_status_display()


# =========================================================
# ORDER ITEM
# =========================================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Store product name separately
    # so old orders remain readable
    # even if product is deleted.

    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    quantity = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    def __str__(self):

        return (
            f"{self.product_name} "
            f"x {self.quantity}"
        )