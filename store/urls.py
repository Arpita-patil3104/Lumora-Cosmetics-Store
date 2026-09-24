from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOME
    # =========================
    path(
        "",
        views.home,
        name="home"
    ),

    # =========================
    # PRODUCTS
    # =========================
    path(
        "products/",
        views.product_list,
        name="product_list"
    ),

    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),

    # =========================
    # AUTHENTICATION
    # =========================
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register_view,
        name="register"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # =========================
    # CART
    # =========================
    path(
        "cart/",
        views.cart_view,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # =========================
    # WISHLIST
    # =========================
    path(
        "wishlist/",
        views.wishlist_view,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist"
    ),

    # =========================
    # CHECKOUT
    # =========================
    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    # =========================
    # ORDERS
    # =========================
    path(
        "orders/",
        views.my_orders,
        name="my_orders"
    ),

    path(
        "orders/<str:order_number>/",
        views.order_detail,
        name="order_detail"
    ),
]