from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
import uuid

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
# HOME
# =========================================================

def home(request):

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
    )

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    featured_products = products.filter(
        is_featured=True
    )[:8]

    bestseller_products = products.filter(
        is_bestseller=True
    )[:8]

    new_arrivals = products.filter(
        is_new_arrival=True
    )[:8]

    # Fallback products
    if not featured_products.exists():
        featured_products = products[:8]

    if not bestseller_products.exists():
        bestseller_products = products[:8]

    if not new_arrivals.exists():
        new_arrivals = products[:8]

    # Wishlist count
    wishlist_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "bestseller_products": bestseller_products,
        "new_arrivals": new_arrivals,
        "product_count": products.count(),
        "wishlist_count": wishlist_count,
    }

    return render(
        request,
        "store/home.html",
        context
    )


# =========================================================
# PRODUCT LIST
# =========================================================

def product_list(request):

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if query:

        products = products.filter(
            Q(name__icontains=query)
            | Q(brand__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category_slug = request.GET.get(
        "category",
        ""
    ).strip()

    selected_category = None

    if category_slug:

        selected_category = get_object_or_404(
            Category,
            slug=category_slug,
            is_active=True
        )

        products = products.filter(
            category=selected_category
        )

    # -----------------------------------------------------
    # BRAND
    # -----------------------------------------------------

    brand = request.GET.get(
        "brand",
        ""
    ).strip()

    if brand:

        products = products.filter(
            brand__iexact=brand
        )

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    sort = request.GET.get(
        "sort",
        ""
    ).strip()

    if sort == "price-low":

        products = products.order_by(
            "sale_price",
            "price"
        )

    elif sort == "price-high":

        products = products.order_by(
            "-sale_price",
            "-price"
        )

    elif sort == "newest":

        products = products.order_by(
            "-created_at"
        )

    elif sort == "rating":

        products = products.order_by(
            "-rating",
            "-reviews_count"
        )

    elif sort == "bestseller":

        products = products.order_by(
            "-is_bestseller",
            "-created_at"
        )

    else:

        products = products.order_by(
            "-created_at"
        )

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    categories = (
        Category.objects
        .filter(is_active=True)
        .order_by("name")
    )

    # -----------------------------------------------------
    # WISHLIST PRODUCT IDS
    # -----------------------------------------------------

    wishlist_product_ids = []

    if request.user.is_authenticated:

        wishlist_product_ids = list(
            Wishlist.objects
            .filter(
                user=request.user,
                product__is_active=True
            )
            .values_list(
                "product_id",
                flat=True
            )
        )

    context = {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": query,
        "selected_brand": brand,
        "selected_sort": sort,
        "wishlist_product_ids": wishlist_product_ids,
    }

    return render(
        request,
        "store/product_list.html",
        context
    )


# =========================================================
# PRODUCT DETAIL
# =========================================================

def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True
    )

    related_products = (
        Product.objects
        .filter(
            category=product.category,
            is_active=True
        )
        .exclude(
            id=product.id
        )
        .select_related("category")
        .order_by(
            "-is_bestseller",
            "-rating",
            "-created_at"
        )[:4]
    )

    # Wishlist status
    is_wishlisted = False

    if request.user.is_authenticated:

        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    context = {
        "product": product,
        "related_products": related_products,
        "is_wishlisted": is_wishlisted,
    }

    return render(
        request,
        "store/product_detail.html",
        context
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Empty fields
        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return redirect("login")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            next_url = request.GET.get(
                "next"
            )

            if next_url:
                return redirect(next_url)

            return redirect("home")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "store/login.html"
    )


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not username or not email or not password:

            messages.error(
                request,
                "Please fill all required fields."
            )

            return redirect("register")

        # -------------------------------------------------
        # PASSWORD MATCH
        # -------------------------------------------------

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        # -------------------------------------------------
        # USERNAME CHECK
        # -------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "Email is already registered."
            )

            return redirect("register")

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Account created successfully. Welcome!"
        )

        return redirect("home")

    return render(
        request,
        "store/register.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")


# =========================================================
# CART
# =========================================================

# =========================================================
# CART
# =========================================================

@login_required
def cart_view(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = (
        cart.items
        .select_related("product")
        .all()
    )

    subtotal = cart.subtotal

    # Free shipping above ₹499
    if subtotal >= 499:
        shipping_charge = 0
    else:
        shipping_charge = 49

    total_amount = (
        subtotal +
        shipping_charge
    )

    context = {
        "cart": cart,

        # Names used by cart.html
        "items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping_charge,
        "total": total_amount,

        # Keep these too, so nothing else depending on them breaks
        "cart_items": cart_items,
        "shipping_charge": shipping_charge,
        "total_amount": total_amount,
    }

    return render(
        request,
        "store/cart.html",
        context
    )


# =========================================================
# ADD TO CART
# =========================================================

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    # -----------------------------------------------------
    # STOCK CHECK
    # -----------------------------------------------------

    if product.stock <= 0:

        messages.error(
            request,
            "Sorry, this product is currently out of stock."
        )

        return redirect(
            "product_detail",
            slug=product.slug
        )

    # -----------------------------------------------------
    # USER CART
    # -----------------------------------------------------

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    # -----------------------------------------------------
    # CART ITEM
    # -----------------------------------------------------

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # -----------------------------------------------------
    # NEW ITEM
    # -----------------------------------------------------

    if created:

        cart_item.quantity = 1
        cart_item.save()

    # -----------------------------------------------------
    # EXISTING ITEM
    # -----------------------------------------------------

    else:

        if cart_item.quantity < product.stock:

            cart_item.quantity += 1
            cart_item.save()

        else:

            messages.warning(
                request,
                "You have reached the available stock limit."
            )

            return redirect("cart")

    messages.success(
        request,
        f"{product.name} added to your bag."
    )

    return redirect("cart")


# =========================================================
# UPDATE CART
# =========================================================

@login_required
def update_cart(request, item_id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    if request.method == "POST":

        try:

            quantity = int(
                request.POST.get(
                    "quantity",
                    1
                )
            )

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please enter a valid quantity."
            )

            return redirect("cart")

        # -------------------------------------------------
        # REMOVE IF ZERO / NEGATIVE
        # -------------------------------------------------

        if quantity <= 0:

            item.delete()

            messages.success(
                request,
                "Product removed from your bag."
            )

            return redirect("cart")

        # -------------------------------------------------
        # STOCK LIMIT
        # -------------------------------------------------

        if quantity > item.product.stock:

            messages.warning(
                request,
                f"Only {item.product.stock} units are available."
            )

            return redirect("cart")

        # -------------------------------------------------
        # UPDATE QUANTITY
        # -------------------------------------------------

        item.quantity = quantity
        item.save()

        messages.success(
            request,
            "Cart updated successfully."
        )

    return redirect("cart")


# =========================================================
# REMOVE FROM CART
# =========================================================

@login_required
def remove_from_cart(request, item_id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    item.delete()

    messages.success(
        request,
        "Product removed from your bag."
    )

    return redirect("cart")


# =========================================================
# WISHLIST
# =========================================================

@login_required
def wishlist_view(request):

    wishlist_items = (
        Wishlist.objects
        .filter(
            user=request.user,
            product__is_active=True
        )
        .select_related(
            "product",
            "product__category"
        )
    )

    context = {
        "wishlist_items": wishlist_items,
        "wishlist_count": wishlist_items.count(),
    }

    return render(
        request,
        "store/wishlist.html",
        context
    )


# =========================================================
# TOGGLE WISHLIST
# =========================================================

@login_required
def toggle_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:

        wishlist_item.delete()

        messages.success(
            request,
            f"{product.name} removed from your wishlist."
        )

    else:

        Wishlist.objects.create(
            user=request.user,
            product=product
        )

        messages.success(
            request,
            f"{product.name} added to your wishlist."
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home"
        )
    )


# =========================================================
# CHECKOUT
# =========================================================

@login_required
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = (
        cart.items
        .select_related("product")
        .all()
    )

    # -----------------------------------------------------
    # EMPTY CART
    # -----------------------------------------------------

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    # -----------------------------------------------------
    # PRICE CALCULATION
    # -----------------------------------------------------

    subtotal = cart.subtotal

    if subtotal >= 499:
        shipping_charge = 0
    else:
        shipping_charge = 49

    total_amount = (
        subtotal +
        shipping_charge
    )

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not all([
            full_name,
            email,
            phone,
            address,
            city,
            state,
            pincode
        ]):

            messages.error(
                request,
                "Please fill all delivery details."
            )

            return redirect("checkout")

        # -------------------------------------------------
        # PINCODE VALIDATION
        # -------------------------------------------------

        if not pincode.isdigit() or len(pincode) != 6:

            messages.error(
                request,
                "Please enter a valid 6-digit pincode."
            )

            return redirect("checkout")

        # -------------------------------------------------
        # STOCK CHECK
        # -------------------------------------------------

        for item in cart_items:

            if item.product.stock < item.quantity:

                messages.error(
                    request,
                    f"Only {item.product.stock} units of "
                    f"{item.product.name} are available."
                )

                return redirect("cart")

        # =================================================
        # CREATE ORDER
        # =================================================

        with transaction.atomic():

            order_number = (
                "ORD-" +
                uuid.uuid4().hex[:10].upper()
            )

            order = Order.objects.create(

                user=request.user,

                order_number=order_number,

                full_name=full_name,

                email=email,

                phone=phone,

                address=address,

                city=city,

                state=state,

                pincode=pincode,

                subtotal=subtotal,

                shipping_charge=shipping_charge,

                total_amount=total_amount,

                status="pending",
            )

            # ---------------------------------------------
            # CREATE ORDER ITEMS
            # ---------------------------------------------

            for item in cart_items:

                product = item.product

                item_total = (
                    product.final_price *
                    item.quantity
                )

                OrderItem.objects.create(

                    order=order,

                    product=product,

                    product_name=product.name,

                    price=product.final_price,

                    quantity=item.quantity,

                    total_price=item_total,
                )

                # -----------------------------------------
                # REDUCE STOCK
                # -----------------------------------------

                product.stock -= item.quantity

                product.save(
                    update_fields=["stock"]
                )

            # ---------------------------------------------
            # CLEAR CART
            # ---------------------------------------------

            cart.items.all().delete()

        messages.success(
            request,
            "Your order has been placed successfully!"
        )

        return redirect(
            "order_detail",
            order_number=order.order_number
        )

    # =====================================================
    # CHECKOUT PAGE
    # =====================================================

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping_charge": shipping_charge,
        "total_amount": total_amount,
    }

    return render(
        request,
        "store/checkout.html",
        context
    )


# =========================================================
# MY ORDERS
# =========================================================

@login_required
def my_orders(request):

    orders = (
        Order.objects
        .filter(
            user=request.user
        )
        .prefetch_related("items")
    )

    context = {
        "orders": orders,
    }

    return render(
        request,
        "store/orders.html",
        context
    )


# =========================================================
# ORDER DETAIL
# =========================================================

@login_required
def order_detail(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        order_number=order_number,
        user=request.user
    )

    context = {
        "order": order,
    }

    return render(
        request,
        "store/order_detail.html",
        context
    )