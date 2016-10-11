from django.conf import settings
from django.db import models
from .campaign import Campaign
from .order import Order
from .reward import Reward


class Update(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=255)
    author = models.CharField(max_length=255, verbose_name="Author Name")
    email = models.EmailField(verbose_name="Author Email")
    text = models.TextField()


class Question(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, verbose_name="Name")
    email = models.EmailField(verbose_name="Email", blank=True)
    text = models.TextField()
    orig = models.ForeignKey('self', related_name='replies', verbose_name='In reply to', blank=True, null=True)
    notify = models.BooleanField(default=True, verbose_name="Notify me on replies")
    team_response = models.BooleanField(default=False, verbose_name="Add the Team Response flag")


class Value(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=7, verbose_name="Currency Abbreviation")
    value = models.FloatField(verbose_name="USD to currency")
    update = models.BooleanField(verbose_name="Update value from API?")
