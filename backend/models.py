from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
]

ADDRESS_CHOICES = [
    ('B', 'Billing'),
    ('S', 'Shipping'),
]


STATE_CHOICES = [
    ('Chittagong', (
            ('cbra', 'Brahmanbaria'),
            ('ccom', 'Comilla'),
            ('clak', 'Lokshmipur'),
            ('cnoa', 'Noakhali'),
            ('cfen', 'Feni'),
            ('ckha', 'Khagrachhari'),
            ('cran', 'Rangamati'),
            ('cban', 'Bandarban'),
            ('cchi', 'Chittagong'),
            ('ccox', "Cox's Bazar"),
        )
     ),
    ('Barisal', (
        ('bbra', 'Barisal'),
        ('bbar', 'Barguna'),
        ('bhol', 'Bhola'),
        ('bjal', 'Jhalokati'),
        ('bpat', 'Patuakhali'),
        ('bpir', 'Pirojpur'),
        )
     ),
    ('Dhaka', (
        ('ddha', 'Dhaka'),
        ('dgha', 'Ghazipur'),
        ('dkis', 'Kishoreganj'),
        ('dman', 'Manikganj'),
        ('dmun', 'Munshiganj'),
        ('dnar', 'Narayanganj'),
        ('dnrs', 'Narasingdi'),
        ('dtan', 'Tangail'),
        ('dfar', 'Faridpur'),
        ('dgop', 'Gopalganj'),
        ('dmad', 'Madaripur'),
        ('draj', 'Rajbari'),
        ('dsha', 'Shariatpur'),
        )
     ),
]

COUNTRY_CHOICES = [
    ('BD', 'Bangladesh'),
]


class Product(models.Model):
    title = models.CharField(max_length=200, blank=False)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="available from")
    description = models.TextField(verbose_name="more info")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=3)
    views = models.PositiveIntegerField(default=0)
    image = models.ImageField()

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1, blank=False)
    is_ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity}  -  {self.product.title}"

    def get_total_price(self):
        return self.quantity * self.product.price

    def get_total_discount_price(self):
        return self.quantity * self.product.discount_price

    def get_saving_price(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_cart_price(self):
        if self.product.discount_price:
            return self.get_total_discount_price()
        else:
            return self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_products = models.ManyToManyField(Cart, related_name='cart')
    is_ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='billing_address')
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='shipping_address')
    is_delivered = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=20)
    is_refund_requested = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def final_order_price(self):
        total = 0
        for cart in self.cart_products.all():
            total += cart.get_final_cart_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100, blank=True)
    country = models.CharField(choices=COUNTRY_CHOICES, max_length=2)
    state = models.CharField(choices=STATE_CHOICES, max_length=4)
    zip_code = models.CharField(max_length=15, blank=True)
    address_type = models.CharField(choices=ADDRESS_CHOICES, max_length=1)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.user.username


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.order.ref_code