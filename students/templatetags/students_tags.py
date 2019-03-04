from django import template
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from students.models import Distribution
from timeline.utils import get_timeslot

register = template.Library()


@register.simple_tag
def get_distribution_tag(user):
    """
    Shows the students distribution in the sidebar

    :param user:
    :return:
    """
    if not user.is_authenticated or user.groups.exists():
        return ''
    # check if user has distributions
    timeslot = get_timeslot()
    try:
        dist = user.distributions.get(TimeSlot=timeslot)
    except Distribution.DoesNotExist:
        return ''
    url = reverse('proposals:details', args=[dist.Proposal.pk])
    html = '<p>You are distributed to the project:</p><a href="{}" class ="button primary" title="{}">{}</a></p>'
    title = truncatechars(dist.Proposal.Title, 25)
    st = format_html(html, url, title, title)
    return st


@register.filter
def get_applications(student):
    """
    Get all applications of a student in this timeslot
    :param student:
    :return:
    """
    return student.applications.filter(Proposal__TimeSlot=get_timeslot())
