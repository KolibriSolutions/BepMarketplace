from django.conf.urls import url
from djangosaml2.views import login

from . import views

#from .forms import CaptchaPasswordResetForm

app_name = 'index'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', login, name='login'),  # internal call to djangosaml2 login
    url(r'^logout/$', views.logout, name='logout'),  # Saml logout doesn't work, so only local logout.
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^feedback/form/$', views.feedbackForm, name='feedbackForm'),
    url(r'^feedback/submit/$', views.feedbackSubmit, name='feedbackSubmit'),
    url(r'^feedback/list/$', views.listFeedback, name='feedbacklist'),
    url(r'^feedback/confirm/(?P<pk>[0-9]+)/$', views.feedbackConfirm, name='feedbackconfirm'),
    url(r'^feedback/close/(?P<pk>[0-9]+)/$', views.feedbackClose, name='feedbackclose'),
    url(r'^about/$', views.about, name='about'),
    url(r'^changesettings/$', views.changeSettings, name='changesettings'),
]