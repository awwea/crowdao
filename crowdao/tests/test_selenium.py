#
# TODO: mock all stripe requests - we are testing the UI here
#

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from django.core.urlresolvers import reverse
from django.conf import settings

from .common import web_test


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    @web_test
    def setUpClass(cls):
        super(MySeleniumTests, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    @web_test
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def setUp(self):
        if settings.DEBUG is False:
            settings.DEBUG = True

    @web_test
    def test_cc_payment(self):
        # we test the payment form with a stripe mockup
        sel = self.selenium
        # first step in payment process: choose which payment method
        # url = reverse('approve_payment')
        url = '/c/CC'
        self.selenium.get(self.live_server_url + url)
        # the error 
        validation_message = self.selenium.find_element_by_id('validate')
        self.assertFalse(validation_message.is_displayed())

        # submit the form
        self.selenium.find_element_by_id('submitbutton').click()

        validation_message = self.selenium.find_element_by_id('validate')
        self.assertTrue(validation_message.is_displayed())
        self.assertIn('error', validation_message.text)

        # now fill in the form as best as we can
        # send 100 cents
        sel.find_element_by_id('amount').send_keys('100')
        # select reward level 
        sel.find_element_by_id('rsel0').click()

        # add credit card info
        for (input_id, value) in [
            ('cc-name', 'Test Name'),
            ('email', 'some@email.com'),
            ('cc-number', '4242424242424242'),
            ('cc-exp', '12/17'),
            ('cc-cvc', '123'),
        ]:
            sel.find_element_by_id(input_id).send_keys(value)

        # submit the form
        sel.find_element_by_id('submitbutton').click()

        # TODO: we wait 10 seconds for an answer from stripe
        # would be better to do some conditional thing..
        from time import sleep
        sleep(5)

        # se should now be on the confirmation screen
        self.assertIn('Confirm', sel.page_source)

        # we confirm
        sel.find_element_by_id('submitbutton').click()

        # the payment is made
        self.assertIn('Thank you', sel.page_source)
        sel.find_element_by_id('backbutton').click()

        # and now we should be back on the home page
        print(sel.current_url)

        print('OK, we now wait some secs for your convenience :-)')
        from time import sleep
        sleep(10)
        # print response
