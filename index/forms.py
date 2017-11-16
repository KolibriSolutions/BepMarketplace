import re

#from captcha.fields import ReCaptchaField
from django import forms
from django.conf import settings
#from django.contrib.auth.forms import PasswordResetForm
#from django.contrib.auth.models import User

from templates import widgets
from .models import FeedbackReport, UserMeta

mailPattern = re.compile(settings.EMAILREGEXCHECK)

#
# class CaptchaPasswordResetForm(PasswordResetForm):
#     email = forms.EmailField(label="Email", max_length=254, widget=widgets.MetroTextInput)
#     captcha = ReCaptchaField()
#
#     def clean_email(self):
#         data = self.cleaned_data['email']
#         if data == '' or data is None:
#             return data
#         email = data.strip('\n').strip()
#         if not mailPattern.match(email.strip('\r')):
#             raise forms.ValidationError("Invalid email address: This should be one TU/e email address")
#         domain = email.strip('\r').split('@')[1]
#         domain_list = ["tue.nl"]
#         if domain not in domain_list:
#             raise forms.ValidationError("Please only enter *@tue.nl email addresses")
#         return data
#
#     def get_users(self, email):
#         users = User.objects.filter(email__iexact=email)
#         return users
#
# class LoginForm(forms.Form):
#     username = forms.CharField(label='Your email address:', max_length=100, min_length=6)
#     password = forms.CharField(label='Your password:', max_length=100)
#
# class StudentLoginForm(LoginForm):
#     captcha = ReCaptchaField()
#     def clean_username(self):
#         data = self.cleaned_data['username']
#         if data == '' or data is None:
#             return data
#         if data[0] != 's':
#             raise forms.ValidationError("Please input a valid TU/e s-number")
#         try:
#             int(data.strip('s'))
#         except:
#             raise forms.ValidationError("Please input a valid TU/e s-number")
#
#         if len(data.strip('s')) != 6:
#             raise forms.ValidationError("Please input a valid TU/e s-number")
#
#         return data

#
# class RegistrationForm(forms.Form):
#     username = forms.CharField(label='UserName:', max_length=100, min_length=2, widget=widgets.MetroTextInput)
#     firstname = forms.CharField(label='First Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
#     lastname = forms.CharField(label='Last Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
#     email = forms.EmailField(label='Email Address:', widget=widgets.MetroEmailInput)
#     backendlogin = forms.BooleanField(label='Backend Login Enabled:', widget=widgets.MetroCheckBox, required=False,
#                                       initial=False)
#     group = forms.ChoiceField(label='Type Staff:', widget=widgets.MetroSelect)
#
#     def __init__(self, groups=[], *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['group'].choices = groups
#
#
# class ProfileEditForm(forms.Form):
#     firstname = forms.CharField(max_length=255, widget=widgets.MetroTextInput)
#     lastname = forms.CharField(max_length=255, widget=widgets.MetroTextInput)


class FeedbackForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Url'].widget.attrs['readonly'] = True

    class Meta:
        model = FeedbackReport
        fields = ['Url', 'Feedback']

        widgets = {
            'Feedback'  : widgets.MetroMultiTextInput,
        }
        labels = {
            'Url': "Page to give feedback on:"
        }

class CloseFeedbackReportForm(forms.Form):
    email = forms.EmailField(label='Sending to:', disabled=True, widget=widgets.MetroTextInput)
    message = forms.CharField(max_length=1024, label='Message:', widget=widgets.MetroMultiTextInput)

# class RegisterType2(forms.Form):
#     firstname = forms.CharField(label='First Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
#     lastname = forms.CharField(label='Last Name:', max_length=100, min_length=1, widget=widgets.MetroTextInput)
#     email = forms.EmailField(label='Email Address:', widget=widgets.MetroEmailInput)
#     captcha = ReCaptchaField()
#
#     def clean_email(self):
#         data = self.cleaned_data['email']
#         domain = data.split('@')[1]
#         domain_list = ["tue.nl",]
#         if domain not in domain_list:
#             raise forms.ValidationError("Please enter an TU/e email address")
#         return data


class settingsForm(forms.ModelForm):

    class Meta:
        model = UserMeta
        fields = [
            'SuppressStatusMails'
        ]
        widgets = {
            'SuppressStatusMails': widgets.MetroCheckBox
        }
        labels = {
            'SuppressStatusMails': "Suppress status emails"
        }
