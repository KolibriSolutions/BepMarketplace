from django.urls import path
from djangosaml2.views import login

from . import views

app_name = 'index'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', login, name='login'),  # internal call to djangosaml2 login
    path('logout/', views.logout, name='logout'),  # Saml logout doesn't work, so only local logout.
    path('profile/', views.profile, name='profile'),
    path('feedback/form/', views.feedback_form, name='feedbackForm'),
    path('feedback/submit/', views.feedback_submit, name='feedbackSubmit'),
    path('feedback/list/', views.list_feedback, name='feedbacklist'),
    path('feedback/confirm/<int:pk>/', views.feedback_confirm, name='feedbackconfirm'),
    path('feedback/close/<int:pk>/', views.feedback_close, name='feedbackclose'),
    path('about/', views.about, name='about'),
    path('profile/settings/', views.user_settings, name='changesettings'),
    path('terms/', views.terms_form, name='termsaccept'),
    path('track/', views.edit_tracks, name='edit_tracks'),
]
