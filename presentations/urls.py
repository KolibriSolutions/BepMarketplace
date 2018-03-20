from django.conf.urls import url
from . import views
# from wkhtmltopdf.views import PDFTemplateView

app_name = 'presentations'

urlpatterns = [
    url(r'^wizard/step1/$', views.presentationswizardstep1, name='presentationswizardstep1'),
    url(r'^wizard/step2/$', views.presentationswizardstep2, name='presentationswizardstep2'),
    url(r'^wizard/step3/$', views.presentationswizardstep3, name='presentationswizardstep3'),
    url(r'^wizard/step4/$', views.presentationswizardstep4, name='presentationswizardstep4'),
    url(r'^list/$', views.presentationsPlanning, name='presentationsplanning'),
    url(r'^listxls/$', views.presentationsPlanningXls, name='presentationsplanningxls'),
    url(r'^$', views.presentationsCalendar, name='presentationscalendar'),
    url(r'^own/$', views.presentationsCalendar, {'own' : True}, name='presentationscalendarown')
]