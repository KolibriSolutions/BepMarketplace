from django.conf.urls import url

from . import views

app_name = 'students'
urlpatterns = [
    url(r'^applications/$', views.listApplications, name='listapplications'),
    url(r'^Application/retract/(?P<application_id>[0-9]+)/$', views.retractApplication, name='retractapplication'),
    url(r'^apply/(?P<pk>[0-9]+)/$', views.applyToProposal, name='apply'),
    url(r'^confirmapplication/(?P<pk>[0-9]+)/$', views.confirmApplication, name='confirmapply'),
    url(r'^Application/prioup/(?P<application_id>[0-9]+)/$', views.prioUp, name='prioUp'),
    url(r'^Application/priodown/(?P<application_id>[0-9]+)/$', views.prioDown, name='prioDown'),
    url(r'^files/add/$', views.addFile, name='addfile'),
    url(r'^files/edit/$', views.editFiles, name='editfiles'),
]