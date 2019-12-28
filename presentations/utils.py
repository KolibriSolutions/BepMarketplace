#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from general_view import get_timeslot, get_timephase_number
from .models import PresentationOptions


def planning_public():
    """
    Check if presentations planning is public visible
    """
    if get_timephase_number() < 5:
        # no distributions yet in phase 5.
        return False
    ts = get_timeslot()
    try:
        options = ts.presentationoptions
    except PresentationOptions.DoesNotExist:
        return False
    if get_timephase_number() == 7 or options.Public:
        return True
    return False
