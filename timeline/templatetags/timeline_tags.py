from django import template
from django.template.base import FilterExpression
from django.template.defaulttags import url

from timeline.utils import get_timephase, get_timephase_number, get_timeslot

register = template.Library()


@register.simple_tag(name='get_timephase')
def get_timephase_tag():
    """

    :return:
    """
    tp = get_timephase()
    if not tp:
        return "No TimePhase Currently"
    return str(tp).split(" in ")[0]


@register.simple_tag(name='get_timephase_number')
def get_timephase_number_tag():
    """

    :return:
    """
    return get_timephase_number()


@register.simple_tag
def get_timeslot_pk():
    """
    Return id of timeslot

    :return:
    """
    ts = get_timeslot()
    if not ts:
        return None
    return ts.pk


@register.simple_tag
def timeslot_exists():
    """

    :return:
    """
    ts = get_timeslot()
    if ts is not None:
        return True
    else:
        return False


@register.simple_tag()
def get_timeslot_end_date():
    """
    The last date in this timeslot, used in the datetimepicker to give a maximum date to select.
    """
    ts = get_timeslot()
    if ts:
        return ts.End
    else:
        return ''


@register.simple_tag(name='get_timeslot')
def get_timeslot_tag():
    """
    String of current timeslot

    :return:
    """
    ts = get_timeslot()
    if not ts:
        return "No TimeSlot Currently"
    return str(ts)


@register.tag
def url_timeslot(parser, token):
    """
    Wrapper around url templatetag which inserts a timeslot argument if a timeslot is present.

    :param parser:
    :param token:
    :return:
    """
    node = url(parser, token)  # default url parser
    ts = get_timeslot()
    if ts:
        node.args.append(FilterExpression(token=str(ts.pk), parser=parser))
    return node
