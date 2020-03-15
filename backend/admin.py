from django.contrib import admin
from backend.models import Product, Cart, Order, Address, Payment, Refund


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_ordered', 'is_delivered', 'is_received',
                    'billing_address', 'shipping_address', 'payment']
    list_display_links = ['user', 'billing_address', 'shipping_address', 'payment']
    list_filter = ['user', 'is_ordered', 'is_delivered', 'is_received']
    search_fields = ['user__username', 'ref_code']


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address', 'country',
                    'state', 'zip_code', 'address_type', 'default']
    list_filter = ['state']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'discount_price', 'category', 'views']
    list_filter = ['category', ]


class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'is_ordered']
    list_filter = ['is_ordered', ]
    search_fields = ['user__username', ]


admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Refund)
