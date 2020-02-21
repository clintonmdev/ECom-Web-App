from django.test import TestCase, Client
from django.urls import reverse
from core.models import Item, OrderItem, Address, Payment, Order, Coupon, Refund
from django.contrib.auth.models import User
import json


class TestViews(TestCase):

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

    def test_home_view_GET(self):
        response = self.client.get(reverse('core:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_product_detail_view_GET(self):
        response = self.client.get(reverse('core:product', args=['item1']))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'product.html')

    def test_product_detail_POST_add_to_cart(self):
        response = self.client.get('/add-to-cart/item1/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            self.order_qs[0].items.first().item.title, 'nike shirt')

    def test_product_detail_POST_remove_from_cart(self):
        self.client.get('/add-to-cart/item1/')
        response = self.client.get('/remove-from-cart/item1/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(
            self.order_qs[0].items.first(), None)
