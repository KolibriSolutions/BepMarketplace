#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import template

from general_view import get_grouptype

register = template.Library()


@register.simple_tag
def get_unverified_users():
    """
    return unverified users for type3staff.

    :return:
    """
    val = get_grouptype('2u').user_set.filter(is_active=True)
    val = val.values_list('usermeta__Fullname', flat=True)
    return val
