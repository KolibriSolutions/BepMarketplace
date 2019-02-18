from django.urls import path

from . import views

app_name = 'professionalskills'

urlpatterns = [
    path('filetype/create/', views.create_filetype, name='filetypecreate'),
    path('filetype/edit/<int:pk>/', views.edit_filetype, name='filetypeedit'),
    path('filetype/delete/<int:pk>/', views.delete_filetype, name='filetypedelete'),
    path('filetype/list/', views.list_filetypes, name='filetypelist'),
    path('studentfiles/<int:pk>/', views.list_student_files, name='liststudentfiles'),
    path('files/', views.list_own_files, name='listownfiles'),
    path('files/type/<int:pk>/all/', views.list_files_of_type, name='listfileoftype'),
    path('files/type/<int:pk>/missing/', views.list_missing_of_type, name='listmissingoftype'),
    path('file/respond/<int:pk>/', views.respond_file, name='respondfile'),

    path('mail/overdue/', views.mail_overdue_students, name='mailoverduestudents'),
    path('print/forms/', views.print_forms, name='printprvforms'),
    path('download/type/<int:pk>/', views.download_all_of_type, name='downloadall'),

    path('group/create/<int:pk>/', views.create_group, name='creategroup'),
    path('group/create/', views.create_group, name='creategroup'),
    path('group/edit/<int:pk>/', views.edit_group, name='editgroup'),
    path('group/listall/<int:pk>/', views.list_groups, name='listgroups'),
    path('group/assign/<int:pk>/', views.assign, name='assignshuffle'),
    path('group/', views.list_own_groups, name='listowngroups'),
    # path('group/switch/<int:frompk>/<int:topk>)/', views.switch_group, name='switchgroups'),
    path('group/switch/<int:pk>/', views.switch_group, name='switchgroups'),
    path('group/members/<int:pk>/', views.list_group_members, name='listgroupmembers'),

    path('extensions/', views.edit_extensions, name='extensions'),
]
