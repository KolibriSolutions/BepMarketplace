#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import template
from django.db.models import Q
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html

from general_view import get_grouptype
from proposals.utils import get_all_proposals, group_administrator_status, can_create_project_fn, can_edit_project_fn, can_downgrade_project_fn
from timeline.utils import get_timeslot

register = template.Library()


@register.simple_tag
def get_pending_tag(user):
    """

    :param user:
    :return:
    """
    # <button> inside <a> is invalid HTML5. MetroUI does not work well with loading-pulse on non-button, so keep it.
    html = "<a href='" + reverse(
        "proposals:pending") + "'><button class=\"button danger loading-pulse\">Pending: {}</button></a>"
    num = 0
    if get_grouptype("2") in user.groups.all():
        num += get_all_proposals().filter(Q(Assistants__id=user.id) & Q(Status__exact=1)).count()
    if get_grouptype("1") in user.groups.all():
        num += get_all_proposals().filter(Q(ResponsibleStaff=user.id) & Q(Status__exact=2)).count()
    num += get_all_proposals().filter(Q(Track__Head=user.id) & Q(Status__exact=3)).count()
    if num == 0:
        return "No pending projects for your attention"
    else:
        return format_html(html.format(num))


@register.simple_tag
def get_personal_tag(user):
    """
    Show the students personal proposals of this timeslot in the sidebar

    :param user:
    :return:
    """
    if not user.is_authenticated or user.groups.exists():
        return ''
    if user.personal_proposal.filter(TimeSlot=get_timeslot()).exists():
        ps = user.personal_proposal.filter(TimeSlot=get_timeslot())
        html = '<p>'
        if ps.count() == 1:
            html += "There is a personal (private) proposal for you. You can view all proposals in the 'proposals' menu but you don't have to do anything with it."
        else:
            html += "There are multiple private proposals for you. Please contact the support staff to remove you from one."
        html += "<br />"
        for p in ps:
            url = reverse('proposals:details', args=[p.pk])
            title = truncatechars(p.Title, 25)
            html += '<a href="{}" class="button primary" title="{}">{}</a><br />'.format(url, title, title)
        html += '</p>'
        return format_html(html)
    return ''


@register.simple_tag
def is_favorite(project, user):
    return project.favorites.filter(User=user).exists()


@register.filter(name='group_administrator_status')
def group_administrator_status_tag(proj, user):
    return group_administrator_status(proj, user)


@register.filter(name='can_create_project')
def can_create_project_tag(user):
    return can_create_project_fn(user)[0]


@register.filter(name='can_edit_project')
def can_edit_project_tag(project, user):
    return can_edit_project_fn(user, project, None)[0]


@register.filter(name='can_downgrade_project')
def can_downgrade_project_tag(project, user):
    return can_downgrade_project_fn(user, project)[0]
