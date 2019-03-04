from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from timeline.utils import get_timephase_number


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
