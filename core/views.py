from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm
import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class HomeView(ListView):
    model = Item
    paginate_by = 9
    template_name = "home.html"


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            return redirect('/')
            messages.error(self.request, 'you do not have an active order')
        return render(self.request, 'order_summary.html')


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # check if the order item is in the order
    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "this item quantity was updated")
            return redirect("core:order-summary")

        else:
            messages.info(request, "this item was added to your cart")
            order.items.add(order_item)
            order_item.quantity = 1
            order_item.save()
            return redirect("core:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        order_item.quantity = 1
        order_item.save()
        messages.info(request, "this item was added to your cart")
    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(
                item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)

            messages.info(request, "this item was removed from your cart")
            return redirect("core:order-summary")

        else:
            messages.info(request, "this item was not in your cart")
            return redirect("core:order-summary", slug=slug)

    else:
        messages.info(request, "you do not have an active order")
        return redirect("core:order-summary", slug=slug)

    return redirect("core:order-summary", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get_or_create(
                item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "this item quantity was updated")
            return redirect("core:order-summary")

        else:
            messages.info(request, "this item was not in your cart")
            return redirect("core:order-summary")

    else:
        messages.info(request, "you do not have an active order")
        return redirect("core:product")

    return redirect("core:product")


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order,
                'form': form,
                'couponform': CouponForm()
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]}
                )

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]}
                )

            return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messges.info("You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                set_default_billing = form.cleaned_data.get(
                    'set_default_billing')
                # check if default shipping
                if use_default_shipping:
                    print('using the default shipping address')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, 'no shipping address available')
                        return redirect('core:checkout')
                else:
                    print('user is entering a new shipping address')

                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_postcode = form.cleaned_data.get(
                        'shipping_postcode')

                    if is_valid_form([shipping_address1, shipping_country, shipping_postcode]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            appartment_address=shipping_address2,
                            country=shipping_country,
                            postcode=shipping_postcode,
                            address_type='S'
                        )
                        # check if set default shipping
                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')

                        if set_default_shipping:
                            address_qs1 = Address.objects.filter(
                                user=self.request.user,
                                address_type='S',
                                default=True
                            )
                            if address_qs1.exists():
                                old_default_shipping_address = address_qs1[0]
                                old_default_shipping_address.default = False
                                old_default_shipping_address.save()
                            shipping_address.default = True
                            shipping_address.save()

                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                        print(form.cleaned_data)

                # Check for same billing
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.address_type = 'B'
                    if set_default_billing:
                        billing_address.default = True
                    else:
                        billing_address.default = False
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                    if set_default_billing:
                        address_qs2 = Address.objects.filter(
                            user=self.request.user,
                            address_type='B',
                            default=True
                        )
                        if address_qs2.exists():
                            old_default_billing_address = address_qs2[0]
                            old_default_billing_address.default = False
                            old_default_billing_address.save()
                        billing_address.default = True
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                else:
                    # check if default billing
                    use_default_billing = form.cleaned_data.get(
                        'use_default_billing')

                    if use_default_billing:
                        print('using the default billing address')
                        address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='B',
                            default=True
                        )
                        if address_qs.exists():
                            billing_address = address_qs[0]
                            order.billing_address = billing_address
                            order.save()
                            print(billing_address)
                        else:
                            messages.info(
                                self.request, 'no billing address available')
                            return redirect('core:checkout')
                    else:
                        print('user is entering a new billing address')

                        billing_address1 = form.cleaned_data.get(
                            'billing_address')
                        billing_address2 = form.cleaned_data.get(
                            'billing_address2')
                        billing_country = form.cleaned_data.get(
                            'billing_country')
                        billing_postcode = form.cleaned_data.get(
                            'billing_postcode')

                        if is_valid_form([billing_address1, billing_country, billing_postcode]):
                            billing_address = Address(
                                user=self.request.user,
                                street_address=billing_address1,
                                appartment_address=billing_address2,
                                country=billing_country,
                                postcode=billing_postcode,
                                address_type='B'
                            )

                            if set_default_billing:
                                address_qs2 = Address.objects.filter(
                                    user=self.request.user,
                                    address_type='B',
                                    default=True
                                )
                                if address_qs2.exists():
                                    old_default_billing_address = address_qs2[0]
                                    old_default_billing_address.default = False
                                    old_default_billing_address.save()
                                billing_address.default = True
                                billing_address.save()
                                order.billing_address = billing_address
                                order.save()

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalide payment option")
                    return redirect('core:checkout')

            messages.warning(self.request, "Failed Checkout")
            return render(self.request, 'checkout.html')
        except ObjectDoesNotExist:
            return redirect('/')
            messages.error(self.request, 'you do not have an active order')
        return redirect('core:order-summary')


class PaymentView(View):
    def get(self, args, **kargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order
            }
            return render(self.request, "payment.html", context)
        else:
            messages.error(
                self.request, 'You have not added a billing address')
            return redirect('core:checkout')

    def post(self, args, **kargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        print(token)
        amount = int(order.get_total() * 100)

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source="tok_mastercard",
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.billing_address = order.billing_address
            payment.save()

            # assign to order
            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            messages.success(self.request, "Your order was successful")
            return redirect("/")
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid Request Error")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication Error")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "API Connection Error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Stripe Error")
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "a serious error")
            return redirect("/")
            # create the payment

        return render(self.request, "payment.html")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This code is not active")
        return redirect('core:checkout')


class AddCouponView(View):
    def post(self, *args, **kargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        # Check for Promo Code
        if order.get_total() >= 30:
            print(order.get_total())
            form = CouponForm(self.request.POST or None)
            if form.is_valid():
                try:
                    code = form.cleaned_data.get('code')

                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    print(code)
                    messages.success(
                        self.request, "The coupon was added succesfuly")
                    return redirect('core:checkout')

                except ObjectDoesNotExist:
                    messages.error(
                        self.request, "You do not have an active order")
                    return redirect("core:checkout")
        else:
            messages.error(
                self.request, "This coupon is only for the orders over $30")
            return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            try:
                # Check for Refund
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                print(order.refund_requested)

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, 'Your request was received')
                return redirect('core:request-refund')
            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist.')
                return redirect('core:request-refund')
