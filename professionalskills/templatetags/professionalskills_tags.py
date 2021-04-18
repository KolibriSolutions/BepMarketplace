#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
from django import template
from django.urls.base import reverse
from django.utils.html import format_html

from distributions.utils import get_distributions
from professionalskills.models import FileType, StudentFile
from students.models import Distribution
from timeline.utils import get_timeslot
from professionalskills.utils import can_respond_file, can_edit_file

register = template.Library()


@register.simple_tag
def get_prv_todo(user):
    """
    get to-do list for prv staff

    :param user:
    :return:
    """
    if not user.is_authenticated:
        return False
    # check if not student
    if not user.groups.exists():
        return False
    ts = get_timeslot()
    des = get_distributions(user, timeslot=ts)
    if not des or not des.exists():
        return 'Nothing to do, you don\'t have students assigned.'
    prvs = FileType.objects.filter(TimeSlot=ts)
    if not prvs.exists():
        return 'Nothing to do, there are no professional skills defined yet.'
    des = des.prefetch_related('Student__usermeta')
    html = '<ul>'
    done = True
    for d in des:
        url = reverse('professionalskills:student', kwargs={'pk': d.pk})
        html += format_html('<li><a href="{}" title="View files">{}:</a><br />', url, d.Student.usermeta.get_nice_name())
        if not d.missing_files().exists() and not d.missing_file_gradings().exists():
            html += f'Finished'
        else:
            html += f'{d.missing_files().count()} files missing, {d.missing_file_gradings().count()} gradings missing.'
            done = False
        html += '</li>'
    html += '</ul>'
    if done:
        html = 'No remaining open tasks.' + html
    else:
        html = "Please review the following items:" + html
    html += '<a href="{}" class ="button primary">{}</a>'
    url = reverse('students:liststudents', kwargs={'timeslot': ts.pk})
    title = "View all"
    html = format_html(html, url, title)
    return html


@register.filter(name='can_edit_file')
def can_edit_file_tag(dist, user):
    return can_edit_file(user, dist)


@register.filter(name='can_respond_file')
def can_respond_file_tag(dist, user):
    return can_respond_file(user, dist)

