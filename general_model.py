import re
import uuid
from datetime import datetime
from django.db.models import Q
from timeline.models import TimeSlot


def get_timeslot_id():
    """
    default timeslot for any model connected to timeslot. Not imported from general_view because circular dependencies.
    """
    return TimeSlot.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))[0].id


def get_ext(filename):
    """
    Get the extension of a given filename
    
    :param filename: a filename
    :return: 
    """
    return filename.split(".")[-1].lower()


def file_delete_default(sender, instance, **kwargs):
    """
    Delete a file
    
    :param sender: 
    :param instance: the file object to delete the file from 
    :param kwargs: 
    :return: 
    """
    try:
        instance.File.delete(False)
    except:
        #in case the file is locked by another process.
        print("Error in removing the file. Only the object will be removed.")


def metro_icon_default(object):
    """
    Gives an icon name from metro ui icon font based on the extension of the filename.
    
    :param object: file object 
    :return: icon name
    """
    extension = get_ext(object.File.name)
    if extension == 'pdf':
        return 'pdf'
    elif extension in ['doc', 'docx', 'odf','rtf']:
        return 'word'
    elif extension in ['jpg', 'jpeg','png','bmp','gif']:
        return 'image'
    elif extension in ['xls', 'xlsx', 'ods']:
        return 'excel'
    elif extension in ['ppt','pptx','odp']:
        return 'powerpoint'
    elif extension in ['tex']:
        return 'code'
    elif extension in ['zip','rar','gz']:
        return 'archive'
    elif extension in ['txt']:
        return 'text'
    return 'empty'


def filename_default(filename):
    """
    Generate a random unique filename.  
    
    :param filename: the original filename, used to get extension from.
    :return: 
    """
    ext = get_ext(filename)
    return "%s.%s" % (uuid.uuid4(), ext)


def clean_text(text):
    """
    Clean ascii control characters and non-breaking-spaces from text.

    :param text: The string to clean.
    :return:
    """
    # almost all except \n \t and \r
    control = r'([\x00-\x08])|([\x0b-\x0c])|([\x0e-\x1f])|([\uFFF0-\uFFFF])|([\u2000-\u200F])|([\u2028-\u202F])|([\x80-\x9F])|([\uE000-\uF8FF])'
    nbsp = r'\xa0'
    try:
        # remove ascii control characters, including replacement character FFFD
        text = re.sub(control, '', text)

        # convert non breaking spaces to regular spaces
        text = re.sub(nbsp, ' ', text)
        return text
    except:
        return ''
    