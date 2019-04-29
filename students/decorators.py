from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from proposals.models import Project
from timeline.utils import get_timephase_number, get_timeslot


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
            raise PermissionDenied("Apply is not possible in this time phase.")
        if request.user.groups.exists():
            raise PermissionDenied("Only students can apply to proposals")
        if request.user.personal_proposal.filter(TimeSlot=get_timeslot()).exists():
            raise PermissionDenied("You cannot apply/retract because there is a private proposal for you.")
        if 'pk' in kw:
            pk = int(kw['pk'])
            prop = get_object_or_404(Project, pk=pk)
            if prop.Private.exists():
                raise PermissionDenied("This proposal is private. It is already assigned.")
        return fn(*args, **kw)

    return wrapper
