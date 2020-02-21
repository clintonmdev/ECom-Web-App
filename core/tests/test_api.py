from rest_framework.test import APITestCase

from core.models import Item, OrderItem
from django.contrib.auth.models import User
import datetime


class ItemTestCase(APITestCase):
    def test_create_item(self):
        # Test User
        now_time = datetime.datetime.now().strftime('%I:%M %p %d %B %Y')
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        # Test Item attributes
        self.item_attrs = {
            "title": "Test Item",
            "price": '123.03',
            "description": "Awesome item",
            "created_date": now_time,
        }
        initial_item_count = Item.objects.count()
        response = self.client.post('/api/v1/items/new', self.item_attrs)
        if response.status_code != 201:
            print(response.data)
        self.assertEqual(
            Item.objects.count(),
            initial_item_count + 1,
        )


class ItemDestroyTestCase(APITestCase):
    def test_destroy_item(self):
        # Test User
        now_time = datetime.datetime.now().strftime('%I:%M %p %d %B %Y')
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        # Test Item attributes
        self.item_attrs = {
            "title": "Test Item",
            "price": '123.03',
            "description": "Awesome item",
            "created_date": now_time,
        }
        response = self.client.post('/api/v1/items/new', self.item_attrs)
        initial_item_count = Item.objects.count()
        test_item_id = Item.objects.all().first().id
        reponse = self.client.delete('/api/v1/items/{}/'.format(test_item_id))
        self.assertEqual(Item.objects.count(), initial_item_count - 1)


class ItemListTestCase(APITestCase):
    def test_list_items(self):
        item_count = Item.objects.count()
        response = self.client.get('/api/v1/items/')
        self.assertEqual(len(response.data['results']), item_count)


class ItemUpdateTestCase(APITestCase):
    def test_update_items(self):
        # Test User
        now_time = datetime.datetime.now().strftime('%I:%M %p %d %B %Y')
        self.user = User.objects.create_user(
            username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        # Test Item attributes
        self.item_attrs = {
            "title": "Test Item",
            "price": '123.03',
            "description": "Awesome item",
            "created_date": now_time,
        }
        response = self.client.post('/api/v1/items/new', self.item_attrs)

        item = Item.objects.all().first()
        response = self.client.patch('/api/v1/items/{}/'.format(item.id),
                                     {
            'title': 'new title',
        },
            format='json',
        )
        updated = Item.objects.get(id=item.id)
        self.assertEqual(updated.title, 'new title')

        # clean up
        del self.user
