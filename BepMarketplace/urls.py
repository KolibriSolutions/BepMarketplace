#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.views.generic.base import RedirectView
from two_factor.urls import urlpatterns as tf_urls

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    # path('js_error_hook/', include('django_js_error_hook.urls')),
    path('', include('index.urls')),
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('api/', include('api.urls')),
    path('canvas/', include('canvas.urls')),
    path('distributions/', include('distributions.urls')),
    path('download/', include('download.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('godpowers/', include('godpowers.urls')),
    path('impersonate/', include('impersonate.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('osiris/data/', include('osirisdata.urls')),
    path('presentations/', include('presentations.urls')),
    path('professionalskills/', include('professionalskills.urls')),
    path('proposals/', include('proposals.urls')),
    path('results/', include('results.urls')),
    # path('shen/', include('shen_ring.urls')),
    path('student/', include('students.urls')),
    path('support/', include('support.urls')),
    path('timeline/', include('timeline.urls')),
    path('tracking/', include('tracking.urls')),
    path('two_factor/', include(tf_urls)),
]

if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
                      path('debug/', include(debug_toolbar.urls)),

                  ] + urlpatterns

# static download path, for unprotected downloads. Not used.
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers.
handler400 = 'index.views.error400'
handler404 = 'index.views.error404'
handler403 = 'index.views.error403'
handler500 = 'index.views.error500'
# handler for 403 csrf in settings.03-security