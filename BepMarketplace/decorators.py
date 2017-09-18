from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from general_view import get_timephase_number, get_grouptype
from proposals.cacheprop import getProp
from proposals.models import Proposal
from support.models import CapacityGroupAdministration


def group_required(*group_names):
    """
    Check whether a user (django-user) is in a given set of django groups. Gives True if in any of the specified groups.
    
    :param group_names: 
    :return: 
    """
    def in_groups(u):
        if u.is_authenticated():
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


def superuser_required():
    """
    True if user is superuser. Redirect to login if not. 
    """
    def is_superuser(u):
        if u.is_authenticated():
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
    Test if a user is a student. A student is a user with 0 groups.

    :return: 
    """
    def is_student(u):
        if u.is_authenticated():
            if not u.groups.exists():
                return True
            else:
                raise PermissionDenied("Only for students")
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
        prop = getProp(pk)
        request = args[0]

        # user needs to be logged in (so no need for login_required on top of this)
        if not request.user.is_authenticated:
            raise PermissionDenied("Please login first")

        # support staf or superusers are always allowed to view
        if get_grouptype("3") in request.user.groups.all() or request.user.is_superuser:
            return fn(*args, **kw)

        # user is staffmember and involved in the proposal
        if prop.ResponsibleStaff == request.user or request.user in prop.Assistants.all() or prop.Track.Head == request.user:
            return fn(*args, **kw)

        # user is secretary (type4) and its the right group
        adms = CapacityGroupAdministration.objects.filter(Members__id=request.user.id)
        if len(adms) > 0:
            for ad in adms:
                if ad.Group == prop.Group:
                    return fn(*args, **kw)

        # if project is published, non private and its the right time phase
        if prop.Status == 4 and (not prop.Private.exists() or request.user in prop.Private.all()):
            # students only in timephase after 2
            if (not request.user.groups.exists()) and get_timephase_number() > 2:
                return fn(*args, **kw)
            # else staff members are allowed to view
            if request.user.groups.exists():
                return fn(*args, **kw)

        raise PermissionDenied("You are not allowed to view this page.")

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
            raise PermissionDenied("Please login first")

        #if no timephase is enabled than forbid editing
        if get_timephase_number() < 0:
            raise PermissionDenied("No editing allowed when system is closed")

        # if timephase is after checking phase no editing is allowed, except for support staff
        if get_timephase_number() > 2 and not get_grouptype("3") in request.user.groups.all():
            raise PermissionDenied("No editing allowed anymore, not right time phase")

        # support staf or superusers are always allowed to edit
        if get_grouptype("3") in request.user.groups.all() or request.user.is_superuser:
            return fn(*args, **kw)

        # track heads are allowed to edit in the create and check phase
        if prop.Track.Head == request.user:
            return fn(*args, **kw)

        # published proposals can never be edited.
        if prop.Status == 4:
            raise PermissionDenied("No editing possible. This proposal is already published")

        # if status is either 1 or 2 and user is assistant edit is allowed in create+check timephase
        if prop.Status < 3 and request.user in prop.Assistants.all():
            return fn(*args, **kw)

        # if status is either 1, 2 or 3(hidden edit, for downgrading api) and user is responsible staff member
        if prop.Status < 4 and prop.ResponsibleStaff == request.user:
            return fn(*args, **kw)

        raise PermissionDenied("You are not allowed to view this page.")

    return wrapper

def can_access_professionalskills(fn):
    """
    Tests if it is the correct timephase and person with access rights to look at profesionalskills

    :param fn:
    :return:
    """

    def wrapper(*args, **kw):
        request = args[0]

        if get_timephase_number() < 5 and get_grouptype("3") not in request.user.groups.all():
            raise PermissionDenied("Student files are not available in this phase")

        return fn(*args, **kw)

    return wrapper


def phase3_only(fn):
    """
    Test if the system is in timephase 3.
    
    :param fn: 
    :return: 
    """
    def wrapper(*args, **kw):
        if get_timephase_number() != 3:
            raise PermissionDenied("Not correct timephase!")
        return fn(*args, **kw)
    return wrapper


def phase7_only(fn):
    """
    Test if the system is in timephase 7
    
    :param fn: 
    :return: 
    """
    def wrapper(*args, **kw):
        if get_timephase_number() != 7:
            raise PermissionDenied("Not correct timephase!")
        return fn(*args, **kw)
    return wrapper
