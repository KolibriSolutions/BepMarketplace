from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('staff/form/<int:pk>/', views.staff_form, name='gradeformstaff'),
    path('staff/form/<int:pk>/<int:step>/', views.staff_form, name='gradeformstaff'),
    path('staff/end/<int:pk>/', views.finalize, name='gradefinal'),
    path('staff/end/<int:pk>/<int:version>/', views.finalize, name='gradefinal'),
]