#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from proposals.models import Project
from .models import Application


def can_apply(fn):
    """
    Test if a student can apply or retract; The system is in timephase 3, user is a student and proposal is nonprivate.

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

        if request.user.groups.exists():
            raise PermissionDenied("Only students can apply to proposals")
        if any([p.nextyear() for p in request.user.personal_proposal.all()]):
            raise PermissionDenied("You cannot apply/retract because there is a private proposal in a future timeslot for you.")
        if 'pk' in kw:
            pk = int(kw['pk'])
            prop = get_object_or_404(Project, pk=pk)
            if request.user.personal_proposal.filter(TimeSlot=prop.TimeSlot).exists():
                raise PermissionDenied(f"There is a private proposal for you in this timeslot ({prop.TimeSlot}). You cannot apply to other projects in this timeslot.")
            if prop.Private.exists():
                raise PermissionDenied("This proposal is private. It is already assigned.")
            if not prop.can_apply():
                raise PermissionDenied("You can no longer apply to proposals of this time slot.")
        if 'application_id' in kw:
            pk = int(kw['application_id'])
            app = get_object_or_404(Application, pk=pk)
            if not app.Proposal.can_apply():
                raise PermissionDenied('Applications of this time slot can no longer be changed.')

        return fn(*args, **kw)

    return wrapper
