import os
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

from firestarter import paypal
import firestarter.views
import firestarter.bitcoin
import firestarter.cc_stripe
import firestarter.paypal
admin.autodiscover()

urlpatterns = [
    url(r'^$', firestarter.views.home, name='home'),
    url(r'^questions/$', firestarter.views.questions, name='questions'),
    url(r'^updates/$', firestarter.views.updates, name='updates'),
    url(r'^c/choose$', firestarter.views.choose, name='choose'),
    # url(r'^firestarter/', include('firestarter.foo.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^admin/', include(admin.site.urls))
]

for x in os.listdir(os.path.join(settings.PROJECT_PATH, 'templates/pages')):
    urlpatterns += [
        url(r'^p/' + x[:-5] + '$', firestarter.views.page, {'pagename': x[:-5]})
    ]

for x in settings.PAY_TYPES:
    if 'CC' in x[0]:
        urlpatterns += [
            url(r'^c/CC$', firestarter.cc_stripe.approve_payment, name='approve_payment'),
            url(r'^c/CC/complete$', firestarter.cc_stripe.complete_payment, name='complete_payment'),
        ]
    elif 'BC' in x[0]:
        urlpatterns += [ 
            url(r'^c/BC$', firestarter.bitcoin.approve_payment, name='approve_payment'),
            url(r'^c/BC/complete$', firestarter.bitcoin.complete_payment, name='complete_payment'),
        ]
    elif 'PP' in x[0]:
        urlpatterns += [ 
            url(r'^c/PP$', firestarter.paypal.approve_payment, name='approve_payment'),
            url(r'^c/PP/confirm$', firestarter.paypal.handle_response, name='handle_response'),
            url(r'^c/PP/complete$', firestarter.paypal.complete_payment, name='complete_payment'),
            url(r'^c/PP/cancel$', firestarter.paypal.cancel, name='cancel')
        ]
