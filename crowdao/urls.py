import os
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from crowdao import paypal
import crowdao.views
import crowdao.bitcoin
import crowdao.cc_stripe
import crowdao.paypal
admin.autodiscover()

urlpatterns = [
    # url(r'^$', crowdao.views.home, name='home'),
    url(r'^$', crowdao.views.HomePage.as_view(), name='page'),
    url(r'^questions/$', crowdao.views.questions, name='questions'),
    url(r'^updates/$', crowdao.views.updates, name='updates'),
    url(r'^c/choose$', crowdao.views.choose, name='choose'),
    # url(r'^crowdao/', include('crowdao.foo.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^admin/', include(admin.site.urls))
]

for x in os.listdir(os.path.join(settings.PROJECT_PATH, 'templates/pages')):
    urlpatterns += [
        url(r'^p/' + x[:-5] + '$', crowdao.views.page, {'pagename': x[:-5]})
    ]

for x in settings.PAY_TYPES:
    if 'CC' in x[0]:
        urlpatterns += [
            url(r'^c/CC$', crowdao.cc_stripe.approve_payment, name='approve_payment'),
            url(r'^c/CC/complete$', crowdao.cc_stripe.complete_payment, name='complete_payment'),
        ]
    elif 'BC' in x[0]:
        urlpatterns += [
            url(r'^c/BC$', crowdao.bitcoin.approve_payment, name='approve_payment'),
            url(r'^c/BC/complete$', crowdao.bitcoin.complete_payment, name='complete_payment'),
        ]
    elif 'PP' in x[0]:
        urlpatterns += [
            url(r'^c/PP$', crowdao.paypal.approve_payment, name='approve_payment'),
            url(r'^c/PP/confirm$', crowdao.paypal.handle_response, name='handle_response'),
            url(r'^c/PP/complete$', crowdao.paypal.complete_payment, name='complete_payment'),
            url(r'^c/PP/cancel$', crowdao.paypal.cancel, name='cancel')
        ]

urlpatterns += [
    url(r'^(?P<path>.*)/$', crowdao.views.Page.as_view(), name='page'),
]
