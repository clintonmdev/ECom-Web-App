from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import HomeView, OrderSummaryView, ItemDetailView, CheckoutView, PaymentView, RequestRefundView, add_to_cart, remove_from_cart


class TestUrls(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse('core:home')
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, HomeView)

    def test_order_summary_url_resolves(self):
        url = reverse('core:order-summary')
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, OrderSummaryView)

    def test_item_detail_url_resolves(self):
        url = reverse('core:product', args=['some-slug'])
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, ItemDetailView)

    def test_checkout_url_resolves(self):
        url = reverse('core:checkout')
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, CheckoutView)

    def test_payment_url_resolves(self):
        url = reverse('core:payment', args=['some-slug'])
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, PaymentView)

    def test_refund_url_resolves(self):
        url = reverse('core:request-refund')
        print(resolve(url))
        self.assertEqual(resolve(url).func.view_class, RequestRefundView)

    def test_add_to_cart_url_resolves(self):
        url = reverse('core:add-to-cart', args=['some-slug'])
        print(resolve(url))
        self.assertEqual(resolve(url).func, add_to_cart)

    def test_add_to_cart_url_resolves(self):
        url = reverse('core:add-to-cart', args=['some-slug'])
        print(resolve(url))
        self.assertEqual(resolve(url).func, add_to_cart)

    def test_remove_from_cart_url_resolves(self):
        url = reverse('core:remove-from-cart', args=['some-slug'])
        print(resolve(url))
        self.assertEqual(resolve(url).func, remove_from_cart)
