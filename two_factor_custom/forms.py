from django.contrib.auth.forms import AuthenticationForm
from two_factor.forms import *

from templates import widgets


class TwoFactorAuthTokenForm(AuthenticationTokenForm):
    otp_token = forms.IntegerField(widget=widgets.MetroNumberInput, label="Token", min_value=1,
                                   max_value=int('9' * totp_digits()))

class TowFactorBackupTokenForm(AuthenticationTokenForm):
    otp_token = forms.CharField(label="Token", widget=widgets.MetroTextInput)

class TwoFactorAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=widgets.MetroTextInput,
    )
    username.widget.attrs.update({'autofocus': 'autofocus'})
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=widgets.MetroPasswordInput,
    )

class TwoFactorDeviceValidationForm(DeviceValidationForm):
    token = forms.IntegerField(label="Token", min_value=1, max_value=int('9' * totp_digits()), widget=widgets.MetroNumberInput)

class TwoFactorTOTPDeviceForm(TOTPDeviceForm):
    token = forms.IntegerField(label="Token", min_value=0, max_value=int('9' * totp_digits()), widget=widgets.MetroNumberInput)
