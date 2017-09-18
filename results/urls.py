from django.conf.urls import url
from . import views

app_name = 'results'

urlpatterns = [
    url(r'^about/$', views.gradeExplanation, name='about'),
    url(r'^staff/form/(?P<pk>[0-9]+)/$', views.gradeFormStaff, name='gradeformstaff'),
    url(r'^staff/form/(?P<pk>[0-9]+)/(?P<step>[0-9]+)/$', views.gradeFormStaff, name='gradeformstaff'),
    url(r'^staff/end/(?P<pk>[0-9]+)/$', views.gradeFinalize, name='gradefinal'),
    url(r'^staff/end/(?P<pk>[0-9]+)/(?P<version>[0-2])/$', views.gradeFinalize, name='gradefinal'),
]