from selenium import webdriver
from core.models import Item, OrderItem, Address, Payment, Order, Coupon, Refund
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
import time


# to run this test you need to download the chromedriver and place it in this folder (/functional_test)


class TestHomePage(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome('functional_test/chromedriver')

    def tearDown(self):
        self.browser.close()

    def test_no_projects_alert_is_displayed(self):
        self.browser.get(self.live_server_url)
        # time.sleep(5)

        # the user requests the page for the first time

        alert = self.browser.find_element_by_class_name('no-item')
        self.assertEquals(
            alert.find_element_by_tag_name('p').text,
            'There is no item available at the moment'
        )
