from django.conf.urls import url
from two_factor.views import (
    BackupTokensView,  PhoneDeleteView, PhoneSetupView,
    ProfileView, QRGeneratorView, SetupCompleteView,
)

from .views import TwoFactorLoginView, TwoFactorDisableView, TwoFactorSetupView

app_name = 'two_factor'

core = [
    url(
        regex=r'^login/$',
        view=TwoFactorLoginView.as_view(),
        name='login',
    ),
    url(
        regex=r'^setup/$',
        view=TwoFactorSetupView.as_view(),
        name='setup',
    ),
    url(
        regex=r'^qrcode/$',
        view=QRGeneratorView.as_view(),
        name='qr',
    ),
    url(
        regex=r'^setup/complete/$',
        view=SetupCompleteView.as_view(),
        name='setup_complete',
    ),
    url(
        regex=r'^backup/tokens/$',
        view=BackupTokensView.as_view(),
        name='backup_tokens',
    ),
    url(
        regex=r'^backup/phone/register/$',
        view=PhoneSetupView.as_view(),
        name='phone_create',
    ),
    url(
        regex=r'^backup/phone/unregister/(?P<pk>\d+)/$',
        view=PhoneDeleteView.as_view(),
        name='phone_delete',
    ),
]

profile = [
    url(
        regex=r'^profile/$',
        view=ProfileView.as_view(),
        name='profile',
    ),
    url(
        regex=r'^disable/$',
        view=TwoFactorDisableView.as_view(),
        name='disable',
    ),
]

urlpatterns = core + profile
