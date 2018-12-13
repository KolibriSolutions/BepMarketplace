from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404

from general_view import get_grouptype
from presentations.models import PresentationTimeSlot
from presentations.utils import planning_public
from proposals.models import Proposal
from proposals.utils import can_edit_project_fn, get_cached_project, can_downgrade_project_fn
from support.utils import group_administrator_status
from support.models import CapacityGroupAdministration
from timeline.utils import get_timephase_number, get_timeslot


def group_required(*group_names):
    """
    Check whether a user (django-user) is in a given set of django groups. Gives True if in any of the specified groups.

    :param group_names:
    :return:
    """

    def in_groups(u):
        if u.is_authenticated:
            if u.groups.filter(name__in=group_names).exists() or u.is_superuser:
                return True
            else:
                raise PermissionDenied("Not part of required group")
        return False

    actual_decorator = user_passes_test(
        in_groups,
        login_url='index:login',
        redirect_field_name='next',
    )
    return actual_decorator


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


def superuser_required():
    """
    True if user is superuser. Redirect to login if not.
    """

    def is_superuser(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
            else:
                raise PermissionDenied("Access Denied: for admins only.")
        return False

    return user_passes_test(
        is_superuser,
        login_url='index:login',
        redirect_field_name='next',
    )


def student_only():
    """
    Test if a user is a student. A student is a user with 0 groups. Students are not allowed in first timephases

    :return:
    """

    def is_student(u):
        if u.is_authenticated:
            if u.groups.exists():
                raise PermissionDenied("This page is only available for students.")
            if get_timephase_number() < 3:
                raise PermissionDenied("The system is not yet open for students.")
            return True
        return False

    return user_passes_test(
        is_student,
        login_url='index:login',
        redirect_field_name='next',
    )


def can_view_proposal(fn):
    """
    Test if a given user is able to see a given proposal.

    :param fn:
    :return:
    """
    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        prop = get_cached_project(pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        # support staf or superusers are always allowed to view
        if get_grouptype("3") in request.user.groups.all() or request.user.is_superuser:
            return fn(*args, **kw)

        # user is staffmember and involved in the proposal
        if prop.ResponsibleStaff == request.user \
                or request.user in prop.Assistants.all() \
                or prop.Track.Head == request.user:
            return fn(*args, **kw)

        # if project is published, non private and its the right time phase
        if prop.Status == 4:
            if not prop.Private.exists() or request.user in prop.Private.all():  # only non-private proposals
                # else staff members are allowed to view public proposals in all timeslots and timephases
                # this includes assessors as they are type1 or type2.
                if request.user.groups.exists():
                    return fn(*args, **kw)
                # students view public proposals or private student views his proposal: Only in timephase after 2
                elif get_timephase_number() > 2 and prop.TimeSlot == get_timeslot():
                    return fn(*args, **kw)
            # assessors are allowed to view status4 private projects if they have to assess it.
            elif planning_public() and \
                    prop.Private.exists() and \
                    request.user.groups.exists() and \
                    prop.TimeSlot == get_timeslot():
                for dist in prop.distributions.all():
                    try:
                        if request.user in dist.presentationtimeslot.Presentations.Assessors.all():
                            return fn(*args, **kw)
                    except PresentationTimeSlot.DoesNotExist:
                        continue

        # user is secretary (type4) and its the right capacity group
        if CapacityGroupAdministration.objects.filter(Q(Members__in=[request.user]) & Q(Group=prop.Group)).exists():
            return fn(*args, **kw)

        raise PermissionDenied("You are not allowed to view this proposal page.")

    return wrapper


def can_edit_proposal(fn):
    """
    Test if a user can edit a given proposal.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        prop = get_object_or_404(Proposal, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_edit_project_fn(request.user, prop, 'ty' in kw)
        if allowed[0] is True:
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper


def can_share_proposal(fn):
    """
    Test if a user can share a given proposal.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        prop = get_object_or_404(Proposal, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_edit_project_fn(request.user, prop, 'ty' in kw)
        if allowed[0] is True:
            return fn(*args, **kw)
        elif (
                request.user == prop.ResponsibleStaff or request.user in prop.Assistants.all() or
                request.user == prop.Track.Head or group_administrator_status(prop, request.user) == 1) and not prop.prevyear():
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper


def can_downgrade_proposal(fn):
    """
    Test if a user can downgrade a given proposal.

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        if 'pk' in kw:
            pk = int(kw['pk'])
        else:
            pk = int(args[1])
        prop = get_object_or_404(Proposal, pk=pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            page = args[0].path
            return redirect_to_login(
                next=page,
                login_url='index:login',
                redirect_field_name='next', )

        allowed = can_downgrade_project_fn(request.user, prop)
        if allowed[0] is True:
            return fn(*args, **kw)
        else:
            raise PermissionDenied(allowed[1])

    return wrapper


def can_access_professionalskills(fn):
    """
    Tests if it is the correct timephase and person with access rights to look at profesionalskills
    # TODO maybe add presentation assessors??

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
        if get_timephase_number() < 6 and \
                get_grouptype("3") not in request.user.groups.all() and \
                get_grouptype("6") not in request.user.groups.all():
            raise PermissionDenied("Student files are not available in this phase")

        if not request.user.groups.exists() and not request.user.distributions.exists():
            raise PermissionDenied("Student files are available after you are distributed to a project.")

        return fn(*args, **kw)

    return wrapper


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

        if get_timephase_number() != 3:
            raise PermissionDenied("Not correct timephase!")
        if request.user.groups.exists():
            raise PermissionDenied("Only students can apply to proposals")
        if request.user.personal_proposal.exists():
            raise PermissionDenied("You cannot apply/retract because there is a private proposal for you.")
        if 'pk' in kw:
            pk = int(kw['pk'])
            prop = get_object_or_404(Proposal, pk=pk)
            if prop.Private.exists():
                raise PermissionDenied("This proposal is private. It is already assigned.")
        return fn(*args, **kw)

    return wrapper
