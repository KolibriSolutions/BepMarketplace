#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from two_factor.views.core import LoginView
from two_factor.views.profile import DisableView

from tracking.models import UserLogin


class TwoFactorLoginView(LoginView):
    """
    The view where a user is logged in using 2fa.
    """

    def done(self, form_list, **kwargs):
        """

        :param form_list:
        :param kwargs:
        :return:
        """
        returnto = super().done(form_list, **kwargs)
        user = self.get_user()
        log = UserLogin()
        log.Subject = user
        log.Twofactor = True
        log.save()

        return returnto


class TwoFactorDisableView(DisableView):
    """Profile page, shows information about current 2fa setup."""
    redirect_url = '/two_factor/profile/'
