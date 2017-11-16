"""
BEPMarketplace URL Configuration

"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^student/', include('students.urls')),
    url(r'^proposals/', include('proposals.urls')),
    url(r'^support/', include('support.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('index.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^tracking/', include('tracking.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^godpowers/', include('godpowers.urls')),
    url(r'^presentations/', include('presentations.urls')),
    url(r'^professionalskills/', include('professionalskills.urls')),
    url(r'^download/', include('download.urls')),
    url(r'^two_factor/', include('two_factor_custom.urls')),
    url(r'^saml2/', include('djangosaml2_custom.urls')),
    url(r'^results/', include('results.urls')),
    url(r'^distributions/', include('distributions.urls')),
]

# if settings.DEBUG and False:
#     import debug_toolbar
#
#     urlpatterns = [
#         url(r'^debug/', include(debug_toolbar.urls)),
#
#     ] + urlpatterns

# static download path, for unprotected downloads. Not used.
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers.
handler400 = 'index.views.error400'
handler404 = 'index.views.error404'
handler403 = 'index.views.error403'
handler500 = 'index.views.error500'
