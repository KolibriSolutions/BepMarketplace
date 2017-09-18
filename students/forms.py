from templates import widgets
from django.forms import ValidationError
from general_form import clean_file_default, FileForm
from general_model import get_ext
from django.shortcuts import get_object_or_404
from professionalskills.models import FileType


def clean_studentfile_default(self):
    """
    Clean function for studentfile form. Checks if the extension is in the allowed extensions for this type file.

    :param self:
    :return:
    """
    try:
        type = get_object_or_404(FileType, pk=self.data['Type'])
    except:
        raise ValidationError("Please select a file type from the dropdown list.")
    file = clean_file_default(self)
    if get_ext(file.name) not in type.get_allowed_extensions():
        raise ValidationError("This file extension is not allowed. Allowed extensions: "+str(type.get_allowed_extensions()))
    return file


class FileAddForm(FileForm):
    """
    Upload a studentfile
    """
    class Meta(FileForm.Meta):
        fields = ['File', 'Caption', 'Type']
        widgets = {
           'File': widgets.MetroFileInput,
           'Caption': widgets.MetroTextInput,
           'Type': widgets.MetroSelect
        }

    def clean_File(self):
        return clean_studentfile_default(self)


class FileEditForm(FileForm):
    """
    Edit a previously uploaded studentfile.
    """
    class Meta(FileForm.Meta):
        fields = ['File', 'Caption','Type']
        widgets = {
            # The custom file widget doesn't work for edit, so use the default.
            'Caption': widgets.MetroTextInput,
            'Type'  : widgets.MetroSelect
        }

    def clean_File(self):
        return clean_studentfile_default(self)
