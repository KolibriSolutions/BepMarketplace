#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import template
from django.urls import reverse

from timeline.utils import get_timephase, get_timephase_number, get_timeslot, get_next_timeslot

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


@register.simple_tag
def url_timeslot(view_name):
    """
    Wrapper around url template tag which inserts a timeslot argument if a timeslot is present.

    :param view_name:
    :return:
    """
    ts = get_timeslot()
    kw = {}
    if ts:
        kw = {'timeslot': ts.pk}
    node = reverse(view_name, kwargs=kw)
    return node


@register.simple_tag(name='get_next_timeslot')
def get_next_timeslot_tag():
    return get_next_timeslot()
