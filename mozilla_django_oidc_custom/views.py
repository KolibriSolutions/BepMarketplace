#  Master Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/MasterMarketplace/blob/master/LICENSE
#
#
import logging
import time

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from mozilla_django_oidc.views import OIDCAuthenticationCallbackView

from general_view import get_grouptype
from index.models import UserMeta
from osirisdata.models import AccessGrant
from timeline.utils import get_timeslot

logger = logging.getLogger('django')


def set_level(user):
    try:
        grant = AccessGrant.objects.get(Email=user.email)
    except AccessGrant.DoesNotExist:
        return

    if grant.Level == 1:
        user.groups.add(get_grouptype("1"))
        user.save()
    if grant.Level == 2:
        if get_grouptype("2u") in user.groups.all():
            user.groups.remove(get_grouptype("2u"))
        user.groups.add(get_grouptype("2"))
        user.save()


def is_staff(user):
    """
    Check whether the user is staff. Staff has a @tue.nl email, students have @student.tue.nl email.
    Some students can have type3staff on BEPMP, as TA support. These should be treated as staff.

    :param user:
    :return:
    """
    if user.email.split('@')[-1].lower() in settings.STAFF_EMAIL_DOMAINS or get_grouptype('3') in user.groups.all():
        return True
    return False


def is_student(user):
    """
    Check whether the user is student. Students have @student.tue.nl email.

    :param user:
    :return:
    """
    if user.email.split('@')[-1].lower() in settings.STUDENT_EMAIL_DOMAINS:
        return True
    return False


def enrolled_osiris(user):
    """
    Check whether the user is enrolled in Osiris for the BEP course

    :param user:
    :return:
    """
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        return False
    return meta.EnrolledBEP


def check_user(request, user):
    meta = user.usermeta  # meta is generated if not exist in signal handler pre_user_save.
    # insert checks on login here
    if user.is_superuser:
        return render(request, 'base.html', status=403, context={
            'Message': 'Superusers are not allowed to login via SSO. Please use 2FA login.'})
    else:
        # block all except supportstaff if there is no timeslot
        # support staff needs login to be able to set a new timeslot or timephase.
        if not get_timeslot() and not get_grouptype('3') in user.groups.all():  # if there isn't a timeslot and not type3
            return render(request, 'base.html', status=403, context={"Message": "Login is currently not available."})

        # login functions for staff and students.
        if is_staff(user):
            # staff, should have valid group
            unverified_grp = get_grouptype("2u")
            set_level(user)  # for accessgrant
            if not user.groups.exists():
                # existing staff member already have groups
                # new staff members get automatically type2staffunverified
                user.groups.add(unverified_grp)
                user.save()
        elif is_student(user):
            if not enrolled_osiris(user):
                return render(request, 'base.html', status=403,
                              context={"Message": "You are not enrolled in our system yet. Please login once through canvas module BEP Marketplace"})
            else:
                if get_timeslot() not in meta.TimeSlot.all():  # user is not active in this timeslot
                    # not in this timeslot so old user, canvas app sets timeslot
                    # this security will fail if canvas does not close off old courses as it does now
                    return render(request, 'base.html', status=403, context={"Message": "You are not active in this time slot. Please login once via the Canvas module."})
        else:
            return render(request, 'base.html', status=403,
                          context={"Message": "Your email address is not known in the system. Login is not allowed. Please contact the support staff."})
    return True


class CustomOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):
    def login_success(self):
        # check if allowed

        response = check_user(self.request, self.user)
        if response is not True:
            return response

        auth.login(self.request, self.user)

        # Figure out when this id_token will expire. This is ignored unless you're
        # using the RenewIDToken middleware.
        expiration_interval = self.get_settings('OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS', 60 * 15)
        self.request.session['oidc_id_token_expiration'] = time.time() + expiration_interval

        return HttpResponseRedirect(self.success_url)

    def login_failure(self):
        logger.error(f'Login failed for {self.user if hasattr(self, "user") else "unknown"}; via {self.request.META.get("HTTP_SEC_FETCH_DEST").lower()}; {self.request.META}')
        return render(request=self.request, template_name='base.html', status=403,
                      context={'Message': 'You are not allowed to login. If you think this is an error, please contact the support. If you tried to login via CANVAS please refresh the page (F5).'})
