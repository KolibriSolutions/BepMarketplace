from django.conf.urls import url
from . import  views

app_name = 'professionalskills'
urlpatterns = [
    url(r'filetype/create/$', views.createFileType, name='filetypecreate'),
    url(r'filetype/edit/(?P<pk>[0-9]+)/$', views.editFileType, name='filetypeedit'),
    url(r'filetype/delete/(?P<pk>[0-9]+)/$', views.deleteFileType, name='filetypedelete'),
    url(r'filetype/list/$', views.listFileType, name='filetypelist'),
    url(r'^studentfiles/(?P<pk>[0-9]+)/$', views.listStudentFiles, name='liststudentfiles'),
    url(r'^files/$', views.listOwnFiles, name='listownfiles'),
    url(r'^files/type/(?P<pk>[0-9]+)/all/$', views.listFilePerType, name='listfileoftype'),
    url(r'^files/type/(?P<pk>[0-9]+)/missing/$', views.listMissingPerType, name='listmissingoftype'),
    url(r'^file/respond/(?P<pk>[0-9]+)/$', views.respondFile, name='respondfile'),
    url(r'^mailoverduestudents/$', views.mailOverDueStudents, name='mailoverduestudents'),
    url(r'^printprvforms/$', views.printPrvForms, name='printprvforms'),
    url(r'^downloadall/(?P<pk>[0-9]+)/$', views.downloadAll, name='downloadall'),

    url(r'^group/create/(?P<pk>[0-9]+)/$', views.createGroup, name='creategroup'),
    url(r'^group/create/$', views.createGroup, name='creategroup'),
    url(r'^group/edit/(?P<pk>[0-9]+)/$', views.editGroup, name='editgroup'),
    url(r'^group/listall/(?P<pk>[0-9]+)/$', views.listGroups, name='listgroups'),
    url(r'^group/assignshuffle/(?P<pk>[0-9]+)/$', views.assignStudents, name='assignshuffle'),
    url(r'^group/listown/$', views.listOwnGroups, name='listowngroups'),
    url(r'^group/switch/(?P<frompk>[0-9]+)/(?P<topk>[0-9]+)/$', views.switchGroup, name='switchgroups'),
    url(r'^group/members/(?P<pk>[0-9]+)/$', views.listGroupMembers, name='listgroupmembers'),
]