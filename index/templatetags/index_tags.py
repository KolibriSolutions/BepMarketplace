from datetime import datetime

from django import template
from django.db.models import Q
from django.utils.html import format_html

from general_view import get_grouptype
from index.models import Broadcast
from proposals.utils import get_writable_admingroups

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_names):
    """
    Check groups for given user.

    :param user:
    :param group_names:
    :return:
    """
    if user.is_anonymous:
        return False
    if user.is_superuser:
        return True
    if group_names == "any":
        if user.groups.exists():
            # if get_grouptype('4') not in user.groups.all() and \
            #         get_grouptype('5') not in user.groups.all() and \
            #         get_grouptype('6') not in user.groups.all():
            #     return True
            # if user.groups.count() > 1:
            #     return True
            # return False
            return True
        else:
            return False
    for group_name in group_names.split(';'):
        if group_name == 'type2staffunverified':
            shortname = '2u'
        else:
            shortname = group_name[4]
        group = get_grouptype(shortname)
        if group in user.groups.all():
            return True
    return False


@register.filter(name='is_track_head')
def is_track_head(user):
    """

    :param user:
    :return:
    """
    if user.is_superuser:
        return True
    if get_grouptype("1") in user.groups.all():
        if user.tracks.exists():
            return True
    return False


@register.simple_tag
def get_broadcasts(user):
    """

    :param user:
    :return:
    """
    msgs = Broadcast.objects.filter((Q(DateBegin__lte=datetime.now()) | Q(DateBegin__isnull=True)) &
                                    (Q(DateEnd__gte=datetime.now()) | Q(DateEnd__isnull=True)) &
                                    (Q(Private=user) | Q(Private__isnull=True))
                                    )
    if not msgs.exists():
        return "No announcements"

    if msgs.count() > 1:
        msg = "<ul>"
        for m in msgs:
            msg += "<li>{}</li>".format(m.Message)
        msg += "</ul>"
    else:
        msg = msgs[0]

    return format_html(str(msg))


@register.simple_tag
def broadcast_available(user):
    """

    :param user:
    :return:
    """
    if not user.is_authenticated:
        return False
    if Broadcast.objects.filter((Q(DateBegin__lte=datetime.now()) | Q(DateBegin__isnull=True)) &
                                (Q(DateEnd__gte=datetime.now()) | Q(DateEnd__isnull=True)) &
                                (Q(Private=user) | Q(Private__isnull=True))
                                ).exists():
        return True
    else:
        return False


@register.filter(name='is_writable_groupadmin')
def is_writable_groupadmin(user):
    return len(get_writable_admingroups(user)) != 0
