from django.conf.urls import url

from . import views

app_name = 'support'

urlpatterns = [
    url(r'^list/$', views.supportListApplicationsDistributions, name='SupportListApplicationsDistributions'),
    url(r'^listdistributionsxls/$', views.supportListDistributionsXls, name='SupportListDistributionsXls'),

    url(r'^mailinglist/$', views.mailinglist, name='mailinglist'),
    url(r'^mailtrackheads/$', views.mailTrackHeads, name='mailtrackheads'),
    url(r'^contentpolicyviolations/$', views.contentpolicy, name='contentpolicy'),
    # url(r'^ectsform/$', views.ECTSForm, name='ectsform'), #deprecated due to osirisdata
    url(r'^stats/$', views.stats, name='stats'),

    # public files
    url(r'^files/add/$', views.addFile, name='addfile'),
    url(r'^files/edit/$', views.editFiles, name='editfiles'),

    # lists
    url(r'^upgradeuser/(?P<pk>[0-9]+)/$', views.upgradeUser, name='upgradeuser'),
    url(r'^downgradeuser/(?P<pk>[0-9]+)/$', views.downgradeUser, name='downgradeuser'),
    url(r'^privateproposals/$', views.listPrivateProposals, name='privateproposals'),
    url(r'^listusers/$', views.listUsers, name='listusers'),
    url(r'^clearcacheuserlist/$', views.clearListUsersCache, name='clearcacheuserlist'),
    url(r'^liststaff/$', views.listStaff, name='liststaff'),
    url(r'^liststaffproposals/(?P<pk>[0-9]+)/$', views.listStaffProposals, name='liststaffproposals'),
    url(r'^liststaffxls/$', views.listStaffXls, name='liststaffXls'),
    url(r'^liststudents/$', views.listStudents, name='liststudents'),
    url(r'^liststudentsxls/$', views.listStudentsXls, name='liststudentsXls'),
    url(r'^listgroupproposals/$', views.listGroupProposals, name='listgroupproposals'),
    url(r'^listproposals/studyadvisor/$', views.listProposalsAdvisor, name='listproposalsadvisor'),
    # url(r'^liststudentsldap/$', views.listStudentsLdap, name='liststudentsldap'),# might be re-introduced when OSIRIS link is finished.
    # url(r'^clearcacheallstudentslist/$', views.clearCacheAllStudentsList, name='clearcacheallstudentslist'),

    url(r'^overruleusermeta/(?P<pk>[0-9]+)/$', views.usermetaOverrule, name='overruleusermeta'),
    url(r'^verifyassistants/$', views.verifyAssistants, name='verifyassistants'),
]
