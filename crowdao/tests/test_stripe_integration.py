import stripe

from django.conf import settings
from django.core.urlresolvers import reverse
from .common import BaseTestCase
from ..models.order import Order, ORDER_STATUS_FINAL, ORDER_STATUS_REIMBURSED, \
    ORDER_STATUS_TRANSFERRED
from ..models.campaign import CAMPAIGN_STATUS_FAILED, Campaign
from .common import web_test

class StripeIntegrationTests(BaseTestCase):

    @web_test
    def test_refund(self):
        # 
        # create a creditcard token for testing purposes
        #
        stripe.api_key = settings.STRIPE_TEST_PRIVATE_KEY
        token = stripe.Token.create(
            card={
                "number": '4242424242424242',
                "exp_month": 12,
                "exp_year": 2017,
                "cvc": '123'
              },
        )

        # create a charge
        charge = stripe.Charge.create(
          amount=2000,
          currency="eur",
          source=token.id,
          description="Charge for joshua.jones@example.com"
        )

        # now we refund
        refund = stripe.Refund.create(charge=charge.id)

        # we expect success
        self.assertEqual(refund.status, 'succeeded')
