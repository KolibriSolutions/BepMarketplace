#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

from django.shortcuts import HttpResponse
from django.urls import path
from django.views.generic import RedirectView
from two_factor.views import LoginView

from . import views

app_name = 'index'
urlpatterns = [
    path('', views.index, name='index'),
    path('two_factor/login/', LoginView.as_view(), name='2falogin'),
    path('login/', RedirectView.as_view(url='/oidc/authenticate/', permanent=False), name='login'),

    path('logout/', views.logout, name='logout'),  # Saml logout doesn't work, so only local logout.
    path('profile/', views.profile, name='profile'),
    path('feedback/form/', views.feedback_form, name='feedback_form'),
    path('feedback/submit/', views.feedback_submit, name='feedback_submit'),
    path('feedback/list/', views.list_feedback, name='list_feedback'),
    path('feedback/confirm/<int:pk>/', views.feedback_confirm, name='confirm_feedback'),
    path('feedback/close/<int:pk>/', views.feedback_close, name='close_feedback'),
    path('about/', views.about, name='about'),
    path('profile/settings/', views.user_settings, name='changesettings'),
    path('terms/', views.terms_form, name='termsaccept'),
    path('robots.txt', lambda r: HttpResponse("User-agent: *\nAllow: /", content_type="text/plain"), name='robots'), # allow all robots.
]
