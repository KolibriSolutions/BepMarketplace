from two_factor.views.core import LoginView, SetupView
from two_factor.views.profile import DisableView
from two_factor.forms import *
from .forms import *
from tracking.models import UserLogin
from django.contrib.auth.models import Group


class TwoFactorLoginView(LoginView):
    """
    The view where a user is logged in using 2fa.
    """
    form_list = (
        ('auth', TwoFactorAuthenticationForm),
        ('token', TwoFactorAuthTokenForm),
        ('backup', TowFactorBackupTokenForm),
    )

    def done(self, form_list, **kwargs):
        returnto = super().done(form_list, **kwargs)
        user = self.get_user()
        if Group.objects.get(name="type3staff") not in user.groups.all():
            log = UserLogin()
            log.Subject = user
            log.Page = '/'
            log.Twofactor = True
            log.save()

        return returnto


class TwoFactorDisableView(DisableView):
    """Profile page, shows information about current 2fa setup."""
    redirect_url = '/two_factor/profile/'


class TwoFactorSetupView(SetupView):
    """
    Form to setup 2fa.
    """
    form_list = (
        ('welcome', Form),
        ('method', MethodForm),
        ('generator', TwoFactorTOTPDeviceForm),
        ('sms', PhoneNumberForm),
        ('call', PhoneNumberForm),
        ('validation', TwoFactorDeviceValidationForm),
        ('yubikey', YubiKeyDeviceForm),
    )