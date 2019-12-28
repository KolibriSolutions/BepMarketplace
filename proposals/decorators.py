#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from general_view import get_grouptype
from presentations.models import PresentationTimeSlot
from presentations.utils import planning_public
from proposals.models import Project
from proposals.utils import get_cached_project, group_administrator_status, can_edit_project_fn, can_downgrade_project_fn, can_create_project_fn
from timeline.utils import get_timephase_number, get_timeslot


def can_view_project(fn):
    """
    Test if a given user is able to see a given project.

    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        proj = get_cached_project(pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next',)

        # support staf or superusers are always allowed to view
        if get_grouptype("3") in request.user.groups.all() or request.user.is_superuser:
            return fn(*args, **kw)

        # user is staffmember and involved in the project
        if proj.ResponsibleStaff == request.user \
                or request.user in proj.Assistants.all() \
                or proj.Track.Head == request.user:
            return fn(*args, **kw)

        # group administrators can view proposal
        if group_administrator_status(proj, request.user) > 0:
            return fn(*args, **kw)

        # if project is published, non private and its the right time phase
        if proj.Status == 4:
            if not proj.Private.exists() or request.user in proj.Private.all():  # only non-private proposals
                # else staff members are allowed to view public proposals in all timeslots and timephases
                # this includes assessors as they are type1 or type2.
                if request.user.groups.exists():
                    return fn(*args, **kw)
                # students view public proposals or private student views his proposal: Only in timephase after 2
                elif get_timephase_number() > 2 and proj.TimeSlot == get_timeslot():
                    return fn(*args, **kw)
            # assessors are allowed to view status4 private projects if they have to assess it.
            elif planning_public() and \
                    proj.Private.exists() and \
                    request.user.groups.exists() and \
                    proj.TimeSlot == get_timeslot():
                for dist in proj.distributions.all():
                    try:
                        if request.user in dist.presentationtimeslot.Presentations.Assessors.all():
                            return fn(*args, **kw)
                    except PresentationTimeSlot.DoesNotExist:
                        continue
        raise PermissionDenied("You are not allowed to view this project page.")

    return wrapper


def can_edit_project(fn):
    """
    Test if a user can edit a given project.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        proj = get_object_or_404(Project, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_edit_project_fn(request.user, proj, 'ty' in kw)
        if allowed[0] is True:
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper


def can_downgrade_project(fn):
    """
    Test if a user can downgrade a given project.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        proj = get_object_or_404(Project, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_downgrade_project_fn(request.user, proj)
        if allowed[0] is True:
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper


def can_create_project(fn):
    """
    User is allowed to create project

    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        page = args[0].path
        request = args[0]
        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )
        allowed = can_create_project_fn(request.user)
        if allowed[0] is True:
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])
    return wrapper

#
# def can_delete_project(fn):
#     def wrapper(*args, **kw):
#         if 'pk' in kw:
#             pk = int(kw['pk'])
#         else:
#             pk = int(args[1])
#         page = args[0].path
#         proj = get_object_or_404(Project, pk=pk)
#         request = args[0]
#
#         # user needs to be logged in (so no need for login_required on top of this)
#         if not request.user.is_authenticated:
#             return redirect_to_login(
#                 next=page,
#                 login_url='index:login',
#                 redirect_field_name='next', )
#
#         allowed = can_delete_project_fn(request.user, proj)
#         if allowed[0] is True:
#             return fn(*args, **kw)
#         else:
#             raise PermissionDenied(allowed[1])
#     return wrapper


def can_share_project(fn):
    """
    Test if a user can share a given project.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        proj = get_object_or_404(Project, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_edit_project_fn(request.user, proj, 'ty' in kw)
        if allowed[0] is True:
            return fn(*args, **kw)
        elif (
                request.user == proj.ResponsibleStaff or request.user in proj.Assistants.all() or
                request.user == proj.Track.Head or group_administrator_status(proj, request.user) > 0) and not proj.prevyear():
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper
