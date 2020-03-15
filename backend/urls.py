from django.urls import path
from backend.views import (
    HomePageView,
    ProductDetailView,
    CrateCartView,
    RemoveCartView,
    OrderSummaryView,
    RemoveSingleCartItemView,
    CheckoutView,
    PaymentView,
    RefundView,
)

app_name = 'backend'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path("product/<int:pk>/", ProductDetailView.as_view(), name='product'),
    path("add-to-cart/<int:product_id>/", CrateCartView.as_view(), name='add_to_cart'),
    path("remove-from-cart/<int:product_id>", RemoveCartView.as_view(), name='remove-from-cart'),
    path("orders/", OrderSummaryView.as_view(), name='orders'),
    path("remove-single-cart-item/<int:product_id>", RemoveSingleCartItemView.as_view(), name='remove-single-cart-item'),
    path("checkout/", CheckoutView.as_view(), name='checkout'),
    path("payment/<payment_method>/", PaymentView.as_view(), name='payment'),
    path("request-refund/", RefundView.as_view(), name='request-refund'),
]
