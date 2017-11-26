from django.conf.urls import url

from . import views

app_name = 'distributions'

urlpatterns = [
    url(r'^distribute/$', views.supportDistributeApplications, name='supportDistributeApplications'),
    url(r'^api/distribute/$', views.distributeApi, name='distribute'),
    url(r'^api/undistribute/$', views.undistributeApi, name='undistribute'),
    url(r'^api/changedistribute/$', views.changeDistributeApi, name='changedistribute'),
    url(r'^distributeproposal/(?P<dtype>[0-9]+)/$', views.proposalOfDistribution, name='distributeproposal'),
    url(r'^maildistributions/$', views.mailDistributions, name='maildistributions'),

]
