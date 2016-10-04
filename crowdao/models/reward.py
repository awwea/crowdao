from django.conf import settings
from django.db import models
from beacon import BeaconCampaign


class Reward(models.Model):
    name = models.CharField(max_length=255, default="", verbose_name='Reward Name')
    min_amount = models.DecimalField(max_digits=8, decimal_places=2, default="", verbose_name="Minimum Amount")
    desc = models.CharField(max_length=255, default="", verbose_name='Reward Description')
    short_desc = models.CharField(max_length=255, default="", verbose_name='Short Reward Description')
    fine_print = models.CharField(max_length=255, default="", verbose_name='Fine Print', blank=True)
    icon_class = models.CharField(max_length=255, default="", verbose_name='Icon Classes', blank=True)
    img = models.URLField(default="", verbose_name='Image URL', blank=True)
