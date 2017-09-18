from django import forms
from django.contrib.auth.models import User, Group

from support.models import CapacityGroupAdministration
from templates import widgets


class groupAdministrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['AdministrationMembers'].queryset = User.objects.all()

    def save(self):
        cleaned_data = self.clean()

        if "AdministrationMembers" not in cleaned_data:
            cleaned_data["AdministrationMembers"] = []

        obj = CapacityGroupAdministration.objects.get(Group=cleaned_data['Group'])

        for member in obj.Members.all():
            if member not in cleaned_data['AdministrationMembers']:
                member.groups.remove(Group.objects.get(name='type4staff'))
                obj.Members.remove(member)
                member.save()

        for member in cleaned_data['AdministrationMembers']:
            if member not in obj.Members.all():
                member.groups.add(Group.objects.get(name='type4staff'))
                obj.Members.add(member)
                member.save()

        obj.save()


    Group = forms.ChoiceField(choices=CapacityGroupAdministration.GroupOptions, widget=widgets.MetroSelect)
    AdministrationMembers = forms.ModelMultipleChoiceField(queryset=User.objects.none(), widget=widgets.MetroSelectMultiple, required=False)