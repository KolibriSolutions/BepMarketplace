#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf.urls import url
from two_factor.views import (
    BackupTokensView, ProfileView, QRGeneratorView, SetupCompleteView, SetupView
)

from .views import TwoFactorLoginView, TwoFactorDisableView

app_name = 'two_factor'

core = [
    url(
        regex=r'^login/$',
        view=TwoFactorLoginView.as_view(),
        name='login',
    ),
    url(
        regex=r'^setup/$',
        view=SetupView.as_view(),
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
