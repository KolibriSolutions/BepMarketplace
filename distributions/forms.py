from django import forms
from templates import widgets


class AutomaticDistributionOptionForm(forms.Form):
    """
    Form to set options for automatic distribution
    """
    dist_choices = ((1, 'By Student'), (2, 'By Project'))
    distribution_type = forms.ChoiceField(widget=widgets.MetroSelect,
                                  help_text='How to run the algorithm. Either look at applications student by student or look at applications by project. Usually, from project gives better results.',
                                  initial=1,
                                  required=False,
                                  choices=dist_choices)
    distribute_random = forms.BooleanField(widget=widgets.MetroCheckBox,
                                           help_text='Whether to distribute leftover students with applications to a random project. Students without applications are never distributed.',
                                           initial=True,
                                           required=False)
    automotive_preference = forms.BooleanField(
        widget=widgets.MetroCheckBox,
        help_text='Whether to give automotive students preference on automotive projects',
        initial=True, required=False)

    def clean_automotive_preference(self):
        return int(self.cleaned_data.get('automotive_preference'))

    def clean_distribute_random(self):
        return int(self.cleaned_data.get('distribute_random'))
