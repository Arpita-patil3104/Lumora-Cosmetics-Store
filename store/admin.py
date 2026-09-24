from django.contrib import admin

from .models import (
    Category,
    Product,
    Wishlist,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


# =========================================================
# CATEGORY ADMIN
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    ordering = (
        "name",
    )


# =========================================================
# PRODUCT ADMIN
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand",
        "category",
        "price",
        "sale_price",
        "stock",
        "rating",
        "is_featured",
        "is_new_arrival",
        "is_bestseller",
        "is_active",
    )

    list_filter = (
        "category",
        "brand",
        "is_featured",
        "is_new_arrival",
        "is_bestseller",
        "is_active",
    )

    search_fields = (
        "name",
        "brand",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "sale_price",
        "stock",
        "is_featured",
        "is_new_arrival",
        "is_bestseller",
        "is_active",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "brand",
                    "category",
                    "description",
                    "image",
                )
            },
        ),

        (
            "Pricing & Inventory",
            {
                "fields": (
                    "price",
                    "sale_price",
                    "stock",
                )
            },
        ),

        (
            "Product Rating",
            {
                "fields": (
                    "rating",
                    "reviews_count",
                )
            },
        ),

        (
            "Store Visibility",
            {
                "fields": (
                    "is_featured",
                    "is_new_arrival",
                    "is_bestseller",
                    "is_active",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )

    ordering = (
        "-created_at",
    )


# =========================================================
# WISHLIST ADMIN
# =========================================================

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "user__username",
        "product__name",
    )

    readonly_fields = (
        "created_at",
    )


# =========================================================
# CART ITEM INLINE
# =========================================================

class CartItemInline(admin.TabularInline):

    model = CartItem

    extra = 0

    autocomplete_fields = (
        "product",
    )

    readonly_fields = (
        "added_at",
    )


# =========================================================
# CART ADMIN
# =========================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "total_items_display",
        "subtotal_display",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "total_items_display",
        "subtotal_display",
    )

    inlines = [
        CartItemInline,
    ]

    def total_items_display(self, obj):

        return obj.total_items

    total_items_display.short_description = "Items"

    def subtotal_display(self, obj):

        return f"₹{obj.subtotal:,.2f}"

    subtotal_display.short_description = "Subtotal"


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "product_name",
        "price",
        "quantity",
        "total_price",
    )

    can_delete = False


# =========================================================
# ORDER ADMIN
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "full_name",
        "email",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "full_name",
        "email",
        "phone",
        "pincode",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
    ]

    fieldsets = (

        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                )
            },
        ),

        (
            "Customer Information",
            {
                "fields": (
                    "full_name",
                    "email",
                    "phone",
                )
            },
        ),

        (
            "Delivery Address",
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),

        (
            "Payment Summary",
            {
                "fields": (
                    "subtotal",
                    "shipping_charge",
                    "total_amount",
                )
            },
        ),

        (
            "Dates",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),

    )

    ordering = (
        "-created_at",
    )


# =========================================================
# ORDER ITEM ADMIN
# =========================================================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product_name",
        "price",
        "quantity",
        "total_price",
    )

    search_fields = (
        "order__order_number",
        "product_name",
    )

    readonly_fields = (
        "order",
        "product",
        "product_name",
        "price",
        "quantity",
        "total_price",
    )