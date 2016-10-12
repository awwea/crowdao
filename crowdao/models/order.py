import uuid

from django.conf import settings
from django.db import models

import stripe

from .reward import Reward

ORDER_STATUS_REIMBURSED = 'REIMBU'
ORDER_STATUS_FINAL = 'FINAL'
ORDER_STATUS_TRANSFERRED = 'TRANSF'

ORDER_STATUS = [
    (ORDER_STATUS_REIMBURSED, 'REIMBURSED'),
    (ORDER_STATUS_FINAL, 'FINALIZED'),
    (ORDER_STATUS_TRANSFERRED, 'Transferred to follow-up campaign'),
]


stripe.api_key = settings.STRIPE_PRIVATE_KEY


class Order(models.Model):
    PAY_TYPES = (
        ('CC', 'Credit Card'),
        ('BC', 'Bitcoin'),
        ('PP', 'PayPal'),
        ('BT', 'Bank Transfer'),
    )

    created_at = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255, default="", verbose_name='Name')
    addr1 = models.CharField(max_length=255, default="", verbose_name='Address 1')
    addr2 = models.CharField(max_length=255, default="", verbose_name='Address 2', blank=True)
    city = models.CharField(max_length=255, default="", verbose_name='City')
    state = models.CharField(max_length=255, default="", verbose_name='State/Province')
    pcode = models.CharField(max_length=255, default="", verbose_name='Postal Code')
    country = models.CharField(max_length=255, default="", verbose_name='Country')
    reward = models.ForeignKey(Reward, related_name='+', verbose_name='Reward Level', blank=True, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default="", verbose_name='Amount')
    ptype = models.CharField(max_length=2, choices=PAY_TYPES, verbose_name='Payment Type')
    pref = models.CharField(max_length=255, default="", verbose_name='Payment Reference', blank=True)
    email = models.EmailField(verbose_name='Email')
    notify = models.BooleanField(verbose_name="Notify me if the project team posts an update?", null=True)
    namecredit = models.CharField(max_length=255, default="", verbose_name='Credit Name', blank=True)
    notes = models.CharField(max_length=255, default="", verbose_name='Notes', blank=True,)

    campaign = models.ForeignKey('Campaign', related_name='orders', blank=True, null=True)
    recurrent = models.BooleanField(verbose_name="Make this a recurrent donation", default=False)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, verbose_name='status')

    charge_id = models.CharField(max_length=255, verbose_name="Stripe Charge id", null=True)

    def pledge(self, card=None):
        """pledge the amount (i.e. charge cc or pay bitcoin or whatever)

        - the card argument (in case of cc payments) is a stripe Token 
        """
        charge = stripe.Charge.create(
            amount=self.amount,
            currency="eur",
            source=card,
            description="Pledge for CrowDAO, thank you!",
        )

        self.charge_id = charge.id
        self.save()

    def reimburse(self):
        #
        # reimburse stripe payment
        #
        if not self.charge_id:
            msg = 'Charge ID not found - cannot reimburse Stripe Payment'
            raise Exception(msg)
        idempotency_key = str(uuid.uuid4())
        refund = stripe.Refund.create(idempotency_key=idempotency_key, charge=self.charge_id)
        if refund.status == 'succeeded':
            # we are happy
            self.status = ORDER_STATUS_REIMBURSED
            self.save()
        else:
            # try again, otherwise give up
            refund = stripe.Refund.create(idempotency_key=idempotency_key, charge=self.charge_id)
            if refund.status == 'succeeded':
                # we are happy
                self.status = ORDER_STATUS_REIMBURSED
                self.save()
            else:
                raise Exception('Could not reimburse: {refund}'.format(refund=refund))

    def finalize(self):
        self.status = ORDER_STATUS_FINAL
        self.save()
