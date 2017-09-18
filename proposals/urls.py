from django.conf.urls import url

from . import views

app_name = 'proposals'
urlpatterns = [
    url(r'^$', views.listProposals, name='list'),
    url(r'^create/$', views.createProposal, name='create'),
    url(r'^addfile/(?P<ty>[a-z]{1})/(?P<pk>[0-9]+)/$', views.addFile, name='addfile'),
    url(r'^editfile/(?P<ty>[a-z]{1})/(?P<pk>[0-9]+)/$', views.editFile, name='editfile'),
    url(r'^edit/$', views.chooseEditProposal, name='chooseedit'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.editProposal, name='edit'),
    url(r'^copy/(?P<pk>[0-9]+)/$', views.copyProposal, name='copy'),
    url(r'^details/(?P<pk>[0-9]+)/$', views.detailProposal, name='details'),
    url(r'^upgradestatus/(?P<pk>[0-9]+)/$', views.upgradeStatus, name='upgradestatus'),
    #url(r'^downgradestatus/(?P<pk>[0-9]+)/$', views.downgradeStatus, name='downgradestatus'),
    url(r'^downgradestatusmessage/(?P<pk>[0-9]+)/$', views.downgradeStatusMessage, name='downgradestatusmessage'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.deleteProposal, name='deleteproposal'),
    url(r'^askdelete/(?P<pk>[0-9]+)/$', views.askDeleteProposal, name='askdeleteproposal'),
    url(r'^pending/$', views.pending, name='pending'),
    url(r'^sharelink/(?P<pk>[0-9]+)/$', views.getShareLink, name='sharelink'),
    url(r'^listtrackproposals/$', views.listTrackProposals, name='listtrackproposals'),
    url(r'^stats/$', views.getProposalStats, name='stats'),
    url(r'^stats/(?P<step>[0-9]+)/$', views.getProposalStats, name='stats'),
    url(r'^stats/general/$', views.getProposalStatsGeneral, name='statsgeneral'),
    url(r'^stats/general/(?P<step>[0-9]+)/$', views.getProposalStatsGeneral, name='statsgeneral'),
]