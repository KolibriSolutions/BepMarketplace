#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from timeline.utils import get_timephase_number


def phase_required(*phase_numbers):
    """
    Check whether the system is in any of the given timephases

    :param phase_numbers: list of ints of allowed phases.
    :return:
    """

    def in_phase(u):
        if u.is_authenticated:
            if get_timephase_number() in phase_numbers:
                return True
            else:
                raise PermissionDenied("This page is not available in the current time phase.")
        return False

    actual_decorator = user_passes_test(
        in_phase,
        login_url='index:login',
        redirect_field_name='next',
    )
    return actual_decorator
