#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from general_view import get_grouptype
from timeline.utils import get_timephase_number


def can_access_professionalskills(fn):
    """
    Tests if it is the correct timephase and person with access rights to look at profesionalskills
    # In future presentation assessors might be added.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        # type 3 and 6 can always view professional skills.
        # Everyone can view it in phase 6 (execution) and later (presenting).
        if get_timephase_number() < 5 and \
                get_grouptype("3") not in request.user.groups.all() and \
                get_grouptype("6") not in request.user.groups.all():
            raise PermissionDenied("Student files are not available in this phase")

        if not request.user.groups.exists() and not request.user.distributions.exists():
            raise PermissionDenied("Student files are available after you are distributed to a project.")

        return fn(*args, **kw)

    return wrapper
