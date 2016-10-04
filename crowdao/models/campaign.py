from django.conf import settings
from django.db import models
from copy import deepcopy

from order import ORDER_STATUS_TRANSFERRED

CAMPAIGN_TYPE_BEACON = 'BEACON'
CAMPAIGN_TYPES = [
    (CAMPAIGN_TYPE_BEACON, 'BEACON'),
]

CAMPAIGN_STATUS_FAILED = 'FAILED'
CAMPAIGN_STATUS_ACTIVE = 'ACTIVE'

CAMPAIGN_STATUS = [
    (CAMPAIGN_STATUS_FAILED, 'FAILED'),
    (CAMPAIGN_STATUS_ACTIVE, 'ACTIVE'),
]


class Campaign(models.Model):
    """A Beacon campaign is a 'recurrent' campaign"""
    name = models.CharField(max_length=255, default="", verbose_name='Campaign Name')
    goal = models.DecimalField(max_digits=8, decimal_places=2, default=500, verbose_name="Goal")
    duration = models.IntegerField(default="7", verbose_name="Duration of the campaign")
    ctype = models.CharField(max_length=6, choices=CAMPAIGN_TYPES, verbose_name='Campagin Type')
    status = models.CharField(max_length=6, choices=CAMPAIGN_STATUS, verbose_name='Campaign status',
        default=CAMPAIGN_STATUS_ACTIVE)
    # if this is a beacon campaign, and it fails, a new campaign will be created: next_campaign
    next_campaign = models.ForeignKey('Campaign', related_name='previous_campaign', null=True)

    def total_pledged(self):
        return self.orders.aggregate(models.Sum('amount'))['amount__sum']

    def goal_reached(self):
        return self.goal - self.total_pledged() <= 0

    def close_campaign(self):
        if self.goal_reached():
            pass
        else:
            # if this is a  beacon campaign, we create a new followup campaign
            assert self.next_campaign == None
            if self.ctype == CAMPAIGN_TYPE_BEACON:
                self.next_campaign = deepcopy(self)
                self.next_campaign.id = None
                self.next_campaign.pk = None
                self.next_campaign.save()

                for order in self.orders.all():
                    if order.recurrent:
                        new_order = deepcopy(order) 
                        new_order.id = None
                        new_order.campaign = self.next_campaign
                        new_order.save()
                        order.status = ORDER_STATUS_TRANSFERRED
                        order.save()
                    else:
                        order.reimburse()
            else:
                # Not a beacon recurrent campaign - reimburse all orders
                for order in self.orders.all():
                    order.reimburse()
            self.status = CAMPAIGN_STATUS_FAILED

