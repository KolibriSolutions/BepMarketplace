from django.urls import path

from . import views

app_name = 'support'

urlpatterns = [

    path('mail/', views.mailing, name='mailinglist'),
    path('mail/trackheads/', views.mail_track_heads, name='mailtrackheads'),

    path('contentpolicy/', views.content_policy, name='contentpolicy'),
    # path('ectsform/', views.ECTSForm, name='ectsform'), #deprecated due to osirisdata
    path('stats/', views.stats, name='stats'),

    # public files
    path('files/add/', views.add_file, name='addfile'),
    path('files/edit/', views.edit_files, name='editfiles'),
    path('files/edit/<int:pk>/', views.edit_file, name='editfile'),
    path('files/delete/<int:pk>/', views.delete_file, name='deletefile'),

    # lists
    path('users/', views.list_users, name='listusers'),
    path('users/<int:pk>', views.user_info, name='userinfo'),
    path('users/clearcache/', views.list_users_clear_cache, name='clearcacheuserlist'),
    path('users/upgrade/<int:pk>/', views.upgrade_user, name='upgradeuser'),
    path('users/downgrade/<int:pk>/', views.downgrade_user, name='downgradeuser'),

    path('applicationsdistributions/', views.list_applications_distributions, name='SupportListApplicationsDistributions'),
    path('distributions/xlsx/', views.list_distributions_xlsx, name='SupportListDistributionsXls'),

    path('staff/', views.list_staff, name='liststaff'),
    path('staff/projects/<int:pk>/', views.list_staff_projects, name='liststaffproposals'),
    path('staff/xlsx/', views.list_staff_xlsx, name='liststaffXls'),
    path('students/', views.list_students, name='liststudents'),
    path('students/xlsx/', views.list_students_xlsx, name='liststudentsXls'),

    path('projects/private/', views.list_private_projects, name='privateproposals'),
    path('projects/group/', views.list_group_projects, name='listgroupproposals'),
    path('projects/studyadvisor/', views.list_studyadvisor_projects, name='listproposalsadvisor'),
    # path('liststudentsldap/', views.listStudentsLdap, name='liststudentsldap'),# might be re-introduced when OSIRIS link is finished.
    # path('clearcacheallstudentslist/', views.clearCacheAllStudentsList, name='clearcacheallstudentslist'),

    path('overruleusermeta/<int:pk>/', views.usermeta_overrule, name='overruleusermeta'),
    path('verifyassistants/', views.verify_assistants, name='verifyassistants'),

    path('nonfull/', views.list_non_full_proposals, name='listnonfullprojects'),
    path('nonfull/<int:timeslot>', views.list_non_full_proposals_xlsx, name='listnonfullprojectsxlsx'),
]
