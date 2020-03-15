import random
import string
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import DetailView, ListView

from backend.forms import CheckOutForm, RefundForm
from backend.models import Product, Cart, Order, Payment, Refund, Address

stripe.api_key = settings.STRIPE_SECRET_KEY


def is_valid_form(fields):
    valid = True
    for field in fields:
        if field == '':
            valid = False
    return valid


class HomePageView(ListView):
    model = Product
    template_name = 'pages/index.html'
    ordering = ['-id']
    paginate_by = 2

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            try:
                cart_count = Cart.objects.filter(user=self.request.user, is_ordered=False).count()
                context['cart_count'] = cart_count
            except ObjectDoesNotExist:
                pass

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'pages/product.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product = Product.objects.get(pk=self.kwargs.get('pk'))
        if self.request.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.request.user, product=product, is_ordered=False)
                context['cart'] = cart
            except ObjectDoesNotExist:
                pass

            try:
                cart_count = Cart.objects.filter(user=self.request.user, is_ordered=False).count()
                context['cart_count'] = cart_count
            except ObjectDoesNotExist:
                pass

        # count product view
        product.views += 1
        product.save()

        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {
                'order': order,
            }
            return render(self.request, 'pages/orders.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Your Cart is Empty!!")
            return redirect('backend:home')


class CrateCartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('product_id'))
        cart, created = Cart.objects.get_or_create(user=self.request.user, product=product, is_ordered=False)
        order_query = Order.objects.filter(user=self.request.user, is_ordered=False)
        if order_query.exists():
            order = order_query[0]
            # checking if the Product is in Cart already
            if order.cart_products.filter(product__id=product.id).exists():
                cart.quantity += 1
                cart.save()
                messages.info(self.request, f'{cart.quantity} {cart.product.title} added to your cart')
                return redirect('backend:orders')
            else:
                order.cart_products.add(cart)
                messages.info(self.request, f'{cart.product.title} - added to cart successful')
        else:
            order = Order.objects.create(user=self.request.user)
            order.cart_products.add(cart)
            messages.info(self.request, 'Item added to cart successful')

        return redirect('backend:product', pk=product.id)


class RemoveSingleCartItemView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('product_id'))
        # query user order
        order_qs = Order.objects.filter(user=self.request.user, is_ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # if the Product is in Order
            if order.cart_products.filter(product__id=product.id).exists():
                cart_product = Cart.objects.filter(user=self.request.user, product=product, is_ordered=False)[0]
                # remove 1 product
                if cart_product.quantity == 0:
                    return redirect('backend:remove-from-cart', product_id=product.id)
                else:
                    cart_product.quantity -= 1
                    cart_product.save()
                    messages.info(self.request, f'1 - "{cart_product.product.title}" removed form cart')
                    return redirect('backend:orders')
            else:
                messages.info(self.request, 'This product is not in your cart.')
                return redirect('backend:orders')
        else:
            messages.info(self.request, 'Your cart is empty. Please add some products!')
            return redirect('backend:orders')


class RemoveCartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('product_id'))
        # query user order
        order_qs = Order.objects.filter(user=self.request.user, is_ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # if the Product is in Order
            if order.cart_products.filter(product__id=product.id).exists():
                cart_product = Cart.objects.filter(user=self.request.user, product=product, is_ordered=False)[0]
                # remove from order
                order.cart_products.remove(cart_product)
                # also remove form cart
                cart_product.delete()

                messages.info(self.request, f'{cart_product.quantity} - "{cart_product.product.title}" removed form cart')
                return redirect('backend:orders')
            else:
                messages.info(self.request, 'This product is not in your cart.')
                return redirect('backend:product', pk=product.id)
        else:
            messages.info(self.request, 'Your cart is empty. Please add some products!')
            return redirect('backend:product', pk=product.id)


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        cart_count = Cart.objects.filter(user=self.request.user, is_ordered=False).count()
        context = {
            'form': form,
            'cart_count': cart_count,
            'order': order,
        }

        # get default shipping address
        default_shipping_address = Address.objects.filter(user=self.request.user, address_type='S', default=True)
        if default_shipping_address.exists():
            context.update({
                'default_shipping_address': default_shipping_address[0]
            })

        # get default billing address
        default_billing_address = Address.objects.filter(user=self.request.user, address_type='B', default=True)
        if default_billing_address.exists():
            context.update({
                'default_billing_address': default_billing_address[0]
            })

        return render(self.request, 'pages/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                # Shipping form actions  -------------------------------------------
                use_default_shipping = form.cleaned_data.get('use_default_shipping_address')
                # check if default address is marked
                if use_default_shipping:
                    address_query = Address.objects.filter(user=self.request.user, address_type='S', default=True)
                    if address_query.exists():
                        shipping_address = address_query[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request.user, "You don't have a default shipping address")
                        return redirect('backend:checkout')
                else:
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_state = form.cleaned_data.get('shipping_state')
                    shipping_zip_code = form.cleaned_data.get('shipping_zip_code')

                    if is_valid_form([shipping_address1, shipping_country, shipping_state, shipping_zip_code]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            state=shipping_state,
                            zip_code=shipping_zip_code,
                            address_type='S',
                        )
                        shipping_address.save()
                        # display notification
                        messages.success(self.request, 'Shipping address added successful')
                        order.shipping_address = shipping_address
                        order.save()

                        # set new default address
                        set_default_shipping_address = form.cleaned_data.get('set_default_shipping_address')
                        if set_default_shipping_address:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, 'Please fill in the required shipping address')
                        return redirect('backend:checkout')
                    # Shipping form action ends  --------------------------------------------

                # Billing form actions  -------------------------------------------------
                use_default_billing_address = form.cleaned_data.get('use_default_billing_address')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()

                    order.billing_address = billing_address
                    order.save()

                # check if default address is true
                elif use_default_billing_address:
                    address_query = Address.objects.filter(user=self.request.user, address_type='B', default=True)
                    if address_query.exists():
                        billing_address = address_query[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request.user, "You don't have a default shipping address fields")
                        return redirect('backend:checkout')
                else:
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_state = form.cleaned_data.get('billing_state')
                    billing_zip_code = form.cleaned_data.get('billing_zip_code')

                    if is_valid_form([billing_address1, billing_country, billing_state, billing_zip_code]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            state=billing_state,
                            zip_code=billing_zip_code,
                            address_type='B',
                        )
                        billing_address.save()
                        # display notification
                        messages.success(self.request, 'Shipping address added successful')
                        order.billing_address = billing_address
                        order.save()

                        # set new default address
                        set_default_billing_address = form.cleaned_data.get('set_default_billing_address')
                        if set_default_billing_address:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, 'Please fill in the required billing address fields')
                        return redirect('backend:checkout')

                    # billing form action ends  -----------------------------------------------------------

                # Check payment method
                payment = form.cleaned_data.get('payment_method')
                if payment == 'str':
                    return redirect('backend:payment', payment_method='stripe')
                elif payment == 'bks':
                    return redirect('backend:payment', payment_method='bkash')
                elif payment == 'con':
                    return redirect('backend:checkout', payment_method='cash-on-delivery')
                else:
                    messages.warning(self.request, 'Payment option invalid!')
                    return redirect('backend:checkout')

            else:
                messages.warning('Form received invalid data. Please try again')
                return redirect('backend:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You have no orders!!')
            return redirect('backend:orders')


def create_ref_code():
    code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    if Order.objects.filter(ref_code=code).exists():
        code = create_ref_code()
    return code


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        context = {
            'order': order,
        }
        return render(self.request, 'pages/payment.html', context)

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            cart = order.cart_products.all()
            amount = int(order.final_order_price() * 100)  # cents
            # create charge
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
            )
            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.final_order_price()
            payment.save()

            # assign payment to order
            order.is_ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            # update cart
            for item in cart:
                item.is_ordered = True
                item.save()

            messages.success(self.request, 'Payment successful!')
            return redirect('/')

        except stripe.error.CardError as e:
            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
            return redirect('/')

        except stripe.error.RateLimitError as e:
            messages.error(self.request, 'Rate Limit Error')
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, 'Invalid request')
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, 'You are not Authenticated')
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, 'Network Error')
            return redirect('/')

        except stripe.error.StripeError as e:
            messages.error(self.request, 'Something went wrong')
            return redirect('/')

        except Exception as e:
            messages.error(self.request, 'Internal error. We have been notified')
            print(e)
            # send error to Admin
            return redirect('/')


class RefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form,
        }
        return render(self.request, 'pages/refund-request.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.is_refund_requested = True
                order.save()
                # save refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.save()

                messages.success(self.request, 'We just received your request. We will contact you later')
                return redirect('backend:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist')
                return redirect('backend:request-refund')


