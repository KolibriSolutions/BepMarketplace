from django.forms.widgets import PasswordInput, Select, TextInput, CheckboxInput, FileInput, DateTimeInput, TimeInput, DateInput


class MetroTextInput(TextInput):
    input_type = 'text'
    template_name = 'widgets/text.html'


class MetroPasswordInput(PasswordInput):
    input_type = 'password'
    template_name = 'widgets/password.html'


class MetroTimeInput(TimeInput):
    """
    A time input with 5 minute steps, using H:i
    converted to a nice picker using jquery datetimepicker in genericForm.html
    """
    input_type = 'text'

    def __init__(self, *args, **kwargs):
        # setting input-control class gives the same metro look, but without the wrapping div around the input
        # the class metrotimepicker is used by the javascript lib
        kwargs['attrs'] = {'class': 'metrotimepicker input-control'}
        super(MetroTimeInput, self).__init__(*args, **kwargs)


class MetroDateInput(DateInput):
    """
    A date input, Date ranging from yesterday to last day of this timeslot. Using Y-m-d
    converted to a nice picker using jquery datetimepicker in genericForm.html
    """
    input_type = 'text'

    def __init__(self, *args, **kwargs):
        # setting input-control class gives the same metro look, but without the wrapping div around the input
        # the class metrodatepicker is used by the javascript lib
        kwargs['attrs'] = {'class': 'metrodatepicker input-control'}
        super(MetroDateInput, self).__init__(*args, **kwargs)


class MetroDateTimeInput(DateTimeInput):
    """
    A date & time input, Date ranging from yesterday to last day of this timeslot. Time in 5 minute steps.
    Format: Y-m-d H:i
    converted to a nice picker using jquery datetimepicker in genericForm.html
    """
    input_type = 'text'

    def __init__(self, *args, **kwargs):
        # setting input-control class gives the same metro look, but without the wrapping div around the input
        # the class metrodatetimepicker is used by the javascript lib
        kwargs['attrs'] = {'class': 'metrodatetimepicker input-control'}
        super(MetroDateTimeInput, self).__init__(*args, **kwargs)


class MetroEmailInput(MetroTextInput):
    input_type = 'email'


class MetroNumberInput(MetroTextInput):
    input_type = 'number'


class MetroNumberInputInteger(MetroNumberInput):
    """
    Client side validation for integer-only input.
    """
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {'step': 0}
        super(MetroNumberInputInteger, self).__init__(*args, **kwargs)


class MetroMultiTextInput(TextInput):
    input_type = 'text'
    template_name = 'widgets/multitext.html'


class MetroSelect(Select):
    input_type = 'select'
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/select_option.html'


class MetroSelectMultiple(Select):
    input_type = 'select'
    allow_multiple_selected = True
    template_name = 'widgets/select.html'
    option_template_name = 'widgets/select_option.html'


class MetroCheckBox(CheckboxInput):
    input_type = 'checkbox'
    template_name = 'widgets/checkbox.html'


class MetroFileInput(FileInput):
    input_type = 'file'
    needs_multipart_form = True
    template_name = 'widgets/file.html'

    def is_initial(self, value):
        """
        Return whether value is considered to be initial value.
        """
        return bool(value and getattr(value, 'url', False))

    def format_value(self, value):
        """
        Return the file object if it has a defined url attribute.
        """
        if self.is_initial(value):
            return value

    def is_image(self, value):
        """

        :param value:
        :return:
        """
        if self.is_initial(value):
            if value.field.__class__.__name__ == 'ImageField':
                return True
        return False

    def get_context(self, name, value, attrs):
        """

        :param name:
        :param value:
        :param attrs:
        :return:
        """
        context = super(MetroFileInput, self).get_context(name, value, attrs)
        context['widget'].update({
            'is_initial': self.is_initial(value),
            'is_image': self.is_image(value),
        })
        return context
