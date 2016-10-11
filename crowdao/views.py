import datetime
import os
import logging
from textwrap import dedent

from django.core.mail import send_mail
from django.shortcuts import render, render_to_response
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.core import urlresolvers
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse

from crowdao.currency import get_btc_rate, dollars_to_eur, dollars_to_gbp, eur_to_dollars, gbp_to_dollars
from crowdao.models import Order, Reward, Update, Question
from crowdao.forms import QuestionForm
from crowdao.utils import get_page
from crowdao import forms
from crowdao import models


PAGES = []
for x in os.listdir(os.path.join(settings.PROJECT_PATH, 'templates/pages')):
    PAGES.append((x[:-5], x[:-5].capitalize()))


def intWithCommas(x):
    if x < 0:
        return '-' + intWithCommas(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)


def questions(request):
    c = get_context()
    c['activepage'] = 'questions'
    c['questions'] = Question.objects.filter(orig=None).order_by('created_at').reverse()
    if request.method == 'POST':
        c['form'] = QuestionForm(request.POST)
        if c['form'].is_valid():
            f = c['form'].save(commit=False)
            if not f.email and f.notify:
                messages.error(request, "Please provide an email address to receive a notification.")
                return render(request, 'comments.html',  RequestContext(request,  c))
            else:
                f.save()
        else:
            messages.error(request, "An error occurred in validation. Please make sure all fields are complete and correct.")
    else:
        c['form'] = QuestionForm()
   
    return render(request, 'comments.html', c)

def updates(request):
    c = get_context()
    c['activepage'] = 'updates'
    c['updates'] = []
    for u in Update.objects.all().order_by('created_at').reverse():
        c['updates'].append((settings.PROJECT_ADDR+'/updates/#'+str(u.pk), u))
    return render(request, 'updates.html', c)

def choose(request):
    proj_name = settings.PROJECT_NAME
    pay_types = settings.PAY_TYPES
    if settings.STOP and (settings.DATE - datetime.datetime.now()).days < 0:
        msg = 'The funding campaign is complete and is no longer accepting new contributions.'
        return render(request, 'error.html', locals())
    else:
        return render(request, 'payment/choose.html', locals())


def page(request, pagename=''):
    c = get_context()
    c['activepage'] = pagename
    return render(request, 'pages/'+pagename+'.html', c)


@receiver(post_save, sender=Update)
def send_notif(sender, instance, **kwargs):
    proj_name = settings.PROJECT_NAME
    proj_addr = settings.PROJECT_ADDR
    for order in Order.objects.all():
        if order.notify:
            send_mail(subject=proj_name+' - New Update', 
                message=get_template('update.txt').render({'update': instance, 'proj_name': proj_name, 'proj_addr': proj_addr}), 
                from_email=settings.NOTIFY_SENDER, 
                recipient_list=[order.email],
                fail_silently=True)

logger = logging.getLogger(__name__)


class Page(TemplateView):
    """Base class for all pages on the site"""
    slug = None
    readmore_buttons = True  # if the text is very long, hide extra paragrapsh behing 'read more' buttons

    def dispatch(self, *args, **kwargs):
        self._set_path_and_page(*args, **kwargs)
        return super(Page, self).dispatch(*args, **kwargs)

    def _set_path_and_page(self, *args, **kwargs):
        self._kwargs = kwargs
        self.path = kwargs.get('path', None)
        try:
            self.page = self.get_page(self.path)
        except Http404:
            self.page = None

    @property
    def template_name(self):
        # if we have a template of the currently requested path, we use that
        # instead of the standard 'page.html'
        if hasattr(self, 'kwargs'):
            path = self.kwargs.get('path', '')
        else:
            path = None
        if path:
            template_name = '%s.html' % path
        if self.slug:
            template_name = '%s.html' % self.slug
        else:
            template_name = 'base.html'
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        template_fullpath = os.path.join(template_dir, 'pages', template_name)
        if os.path.exists(template_fullpath):
            return os.path.join('pages', template_name)

        # if we did not find a custom template, we return the standard one
        if getattr(self, '_template_name', None):
            return self._template_name
        return 'page.html'

    def get_page(self, path=None):
        """try to find a BasicPage object with a slug corresponding to path or self.slug"""
        if path:
            slug = path
        else:
            slug = self.slug
        if slug:
            return get_page(slug)

    def get_pages(self):
        pages = models.Page.objects
        return pages.all()

    def get_context_data(self, path=None, **kwargs):
        page = self.page
        pages = self.get_pages()
        pages_in_menu = [p for p in pages if p.slug not in ['home']]
        context = {
            'path': path,
            'page': page,
            'pages': pages,
            'pages_in_menu': pages_in_menu,
            'settings': settings,
            'home_page': get_page('home'),
            'admin_link': admin_link(page),
            'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', None),
            'home_prefix': '..',
            'request': self.request,
        }
        return context


class HomePage(Page):
    slug = 'home'

    @property
    def template_name(self):
        template_name = 'home.html'
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        template_fullpath = os.path.join(template_dir, template_name)
        return template_fullpath

    def get_context_data(self, *args, **kwargs):
        c = super(HomePage, self).get_context_data(*args, **kwargs)
        total = Order.objects.all().aggregate(Sum('amount'))['amount__sum']
        pct = ((100 * float(total) / float(settings.GOAL)) if total else 0)
        c.update({
            'activepage': 'home',
            'goal': intWithCommas(settings.GOAL),
            'backers': Order.objects.count(),
            'pct': pct,
            'pct_disp': (int(pct) if total else 0),
            'total': (intWithCommas(int(total)) if total else '0'),
            # 'pages': PAGES,
            'nopay': (True if settings.STOP and (settings.DATE - datetime.datetime.now()).days < 0 else False),
            'days': (settings.DATE - datetime.datetime.now()).days,
            'rewards': sorted(Reward.objects.all(), key=lambda i: i.min_amount),
            'rewards_disclaimer': settings.REWARDS_DISCLAIMER,
            'unum': Update.objects.all().count(),
            'qnum': Question.objects.all().count(),
            'proj_name': settings.PROJECT_NAME,
            'proj_addr': settings.PROJECT_ADDR
            })
        return c

def admin_link(page):
    if page:
        return urlresolvers.reverse('admin:crowdao_page_change', args=[page.pk])