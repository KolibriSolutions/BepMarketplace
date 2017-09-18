from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [
    url(r'^upgradestatus/(?P<pk>[0-9]+)/$', views.upgradeStatusApi, name='upgradestatus'),
    url(r'^downgradestatus/(?P<pk>[0-9]+)/$', views.downgradeStatusApi, name='downgradestatus'),
    url(r'^verify/assistant/(?P<pk>[0-9]+)/$', views.verifyAssistant, name='verifyassistant'),
    url(r'^getgroupadmins/$', views.getGroupAdmins, name='getgroupadmins'),
    url(r'^getgroupadmins/(?P<group>[a-zA-Z]+)/$', views.getGroupAdmins, name='getgroupadminsarg'),
    url(r'^share/(?P<token>[0-9A-Za-z_\-:]+)/$', views.viewShareLink, name='viewsharelink'),
    url(r'^listproposals/$', views.getPublishedList, name='listpublished'),
    url(r'^listproposals/group/$', views.getPublishedListPerGroup, name='listpublishedpergroup'),
    url(r'^listproposals/titles/$', views.getPublishedTitles, name='listpublishedtitles'),
    url(r'^proposaldetail/(?P<pk>[0-9]+)/$', views.getPublishedDetail, name='getpublisheddetail'),
]
