from django.test import TestCase, Client
from core.models import Item, OrderItem, Address, Payment, Order, Coupon, Refund
from django.contrib.auth.models import User
from django.urls import reverse


class TestModels(TestCase):
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

    def test_item_get_absolute_url(self):
        self.assertEquals(self.test_item.get_absolute_url(),
                          reverse('core:product', args=['item1']))

    def test_item_get_add_to_cart_url(self):
        self.assertEquals(self.test_item.get_add_to_cart_url(),
                          reverse('core:add-to-cart', args=['item1']))

    def test_get_final_price(self):
        self.client.get('/add-to-cart/item1/')
        self.assertEquals(
            self.order_qs[0].items.first().get_final_price(), 800)
