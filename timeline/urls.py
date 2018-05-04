from django.urls import path

from . import views

app_name = 'timeline'

urlpatterns = [
    path('timeslot/list/', views.list_timeslots, name='list_timeslots'),
    path('timeslot/add/', views.add_timeslot, name='add_timeslot'),
    path('timeslot/<int:timeslot>/', views.edit_timeslot, name='edit_timeslot'),
    path('timeslot/<int:timeslot>/list/', views.list_timephases, name='list_timephases'),
    path('timeslot/<int:timeslot>/add/', views.add_timephase, name='add_timephase'),
    path('timephase/<int:timephase>/', views.edit_timephase, name='edit_timephase'),
]
