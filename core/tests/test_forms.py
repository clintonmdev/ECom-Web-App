from django.test import TestCase, Client
from core.models import Item, OrderItem, Address, Payment, Order, Coupon, Refund
from django.contrib.auth.models import User
from django.urls import reverse
from core.forms import CheckoutForm


class TestForms(TestCase):
    def setUp(self):
        self.client = Client()
        # Test Item
        self.test_item = Item.objects.create(
            title='nike shirt',
            price=10000,
            discount_price=800,
            category='S',
            label='D',
            slug='item1',
            description='this is the new nike shirt',
            image='hh.jpg'
        )
        # Test User
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        self.order_qs = Order.objects.filter(user=self.user, ordered=False)

        # Test cart with item
        self.client.get('/add-to-cart/item1/')

    def test_checkout_form_valid(self):
        form = CheckoutForm(
            {'shipping_address': 'Avenue du pondu', 'shipping_address2': '33', 'shipping_country': 'AS', 'shipping_postcode': '5000', 'same_billing_address': False, 'set_default_shipping': False, 'use_default_shipping': False,
                'payment_option': 'S', 'billing_address': 'Mont fleury', 'billing_address2': '44', 'billing_country': 'AL', 'billing_postcode': '7000', 'set_default_billing': False, 'use_default_billing': False}
        )
        self.assertTrue(form.is_valid(), True)
