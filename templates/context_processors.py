#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.conf import settings


def general(request=None):
    return {
        'DOMAIN': settings.DOMAIN,
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'NAME': settings.NAME_PRETTY,
    }


def debugsetting(request=None):
    """

    :return:
    """
    return {
        'DEBUG': settings.DEBUG
    }
