#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('about/<int:pk>/', views.about, name='about'),
    path('staff/form/<int:pk>/', views.staff_form, name='gradeformstaff'),
    path('staff/form/<int:pk>/<int:step>/', views.staff_form, name='gradeformstaff'),
    # path('staff/file/<int:pk>/', views.staff_form_file, name='gradeformstafffiles'),
    # path('staff/file/<int:pk>/<int:step>/', views.staff_form_file, name='gradeformstafffiles'),
    path('staff/finalize_preview/<int:pk>/', views.finalize_preview, name='gradefinalpreview'),
    path('staff/finalize_preview/<int:pk>/<int:version>/', views.finalize_preview, name='gradefinalpreview'),
    path('staff/end/<int:pk>/', views.finalize, name='gradefinal'),
    path('staff/end/<int:pk>/<int:version>/', views.finalize, name='gradefinal'),


    path('category/list/', views.list_categories, name='list_categories'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('category/<int:pk>/list/', views.list_aspects, name='list_aspects'),
    path('category/<int:pk>/add/', views.add_aspect, name='add_aspect'),
    path('aspect/<int:pk>/', views.edit_aspect, name='edit_aspect'),
    path('aspect/delete/<int:pk>/', views.delete_aspect, name='delete_aspect'),

    path('copy/<int:pk>/', views.copy, name='copy'),
    path('copy/', views.copy, name='copy_overview'),

]
