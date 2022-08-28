#  Master Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/MasterMarketplace/blob/master/LICENSE

from django.apps import AppConfig


class MozillaDjangoOidcCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mozilla_django_oidc_custom'
