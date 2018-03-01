from datetime import datetime

from django import template
from django.contrib.auth.models import Group
from django.db.models import Q
from django.template.defaultfilters import truncatechars
from django.urls.base import reverse
from django.utils import timezone
from django.utils.html import format_html

from general_view import get_grouptype
from proposals.utils import get_all_proposals
from index.models import Broadcast
from presentations.models import PresentationTimeSlot, PresentationSet
from timeline.utils import get_timeslot, get_timephase, get_timephase_number

register = template.Library()


@register.filter(name="index")
def index(List, i):
    """

    :param List:
    :param i:
    :return:
    """
    return List[int(i)]

@register.filter(name='tolist')
def tolist(object):
    return list(object)


@register.filter(name='has_group')
def has_group(user, group_names):
    """

    :param user:
    :param group_names:
    :return:
    """
    if user.is_superuser:
        return True
    if group_names == "any":
        if user.groups.exists():
            if Group.objects.get(name='type4staff') not in user.groups.all() and \
                Group.objects.get(name='type5staff') not in user.groups.all() and \
                Group.objects.get(name='type6staff') not in user.groups.all():
                return True
            if user.groups.count() > 1:
                return True
            return False
        else:
            return False
    for group_name in group_names.split(';'):
        group = Group.objects.get(name=group_name)
        if group in user.groups.all():
            return True

    return False


@register.filter(name='is_trackhead')
def is_trackhead(user):
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
def getPending(user):
    """

    :param user:
    :return:
    """
    html = "<a href='"+reverse("proposals:pending")+"'><button class=\"button danger loading-pulse\">Pending: {}</button></a>"
    num = 0

    if get_grouptype("2")in user.groups.all():
        num += get_all_proposals().filter(Q(Assistants__id=user.id) & Q(Status__exact=1)).count()
    if get_grouptype("1") in user.groups.all():
        num += get_all_proposals().filter(Q(ResponsibleStaff=user.id) & Q(Status__exact=2)).count()
    num += get_all_proposals().filter(Q(Track__Head=user.id) & Q(Status__exact=3)).count()
    if num == 0:
        return "No pending proposals for your attention"
    else:
        return format_html(html.format(num))


@register.simple_tag
def GetPhase():
    """

    :return:
    """
    tp = get_timephase()
    if not tp:
        return "No TimePhase Currently"
    return str(tp).split(" in ")[0]


@register.simple_tag
def GetPhaseNumber():
    """

    :return:
    """
    return get_timephase_number()


@register.simple_tag
def GetHash():
    """

    :return:
    """
    try:
        with open("githash", "r") as stream:
            h = stream.readlines()[0].strip('\n')
        return h[:10]
    except:
        return "None"


@register.simple_tag
def GetSlot():
    """

    :return:
    """
    ts = get_timeslot()
    if not ts:
        return "No TimeSlot Currently"
    return str(ts)


@register.simple_tag
def isThereTimeslot():
    """

    :return:
    """
    ts = get_timeslot()
    if ts is not None:
        return True
    else:
        return False


@register.simple_tag
def GetBroadcast(user):
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
def GetBroadcastStatus(user):
    """

    :param user:
    :return:
    """
    if not user.is_authenticated():
        return False
    if Broadcast.objects.filter((Q(DateBegin__lte=datetime.now()) | Q(DateBegin__isnull=True)) &
                             (Q(DateEnd__gte=datetime.now()) | Q(DateEnd__isnull=True)) &
                             (Q(Private=user) | Q(Private__isnull=True))
                             ).exists():
        return True
    else:
        return False


@register.simple_tag
def GetDistribution(user):
    """

    :param user:
    :return:
    """
    if not user.is_authenticated():
        return False
    # check if student
    if user.groups.exists():
        return False
    # check if user has distributions
    timeslot = get_timeslot()
    try:
        dist = user.distributions.get(Timeslot=timeslot)
    except:
        return False

    url = reverse('proposals:details', args=[dist.Proposal.pk])
    html = '<p>You are distributed to the proposal:</p><a href="{}" class ="button primary">{}</a></p>'
    title =  truncatechars(dist.Proposal.Title,30)
    st = format_html(html, url, title)
    return st


@register.simple_tag()
def GetEndDate():
    """
    The last date in this timeslot, used in the datetimepicker to give a maximum date to select.
    """
    ts = get_timeslot()
    if ts:
        return ts.End
    else:
        return ''

@register.simple_tag
def GetPresentationStudent(user):
    """
    Displays the presentation for a student
    :param user:
    :return:
    """
    if not user.is_authenticated():
        return False
    #check if student
    if user.groups.exists():
        return False
    timeslot = get_timeslot()
    tp = get_timephase()
    try:
        if timeslot.presentationoptions.Public or tp == 7:
            #check if user has presentations
            try:
                t = PresentationTimeSlot.objects.get(Distribution__Student= user)
                start = timezone.localtime(t.DateTime).strftime("%A %d %B %Y %H:%M")
                room = t.Presentations.PresentationRoom
            except:
                return "Your presentation is not (yet) planned."

            url = reverse('presentations:presentationscalendar')
            title = "View all presentations"
            html = '<p>Your presentation is on {} in {}</p>' \
                   '<a href="{}" class ="button primary">{}</a></p>'
            st = format_html(html, start, room, url, title)
            return st
        else:
            return "Your presentation timeslot will appear here when the planning becomes public."
    except:
        return "Your presentation timeslot will appear here when the planning becomes public."


@register.simple_tag
def GetPresentationStaff(user):
    """
    Displays the presentation for a student
    :param user:
    :return:
    """
    if not user.is_authenticated():
        return False
    # check if not student
    if not user.groups.exists():
        return False
    timeslot = get_timeslot()
    tp = get_timephase()

    try:
        if timeslot.presentationoptions.Public or tp == 7:
            if is_trackhead(user):
                # check if trackhead has presentations
                try:
                    t = PresentationSet.objects.filter(Track__in=user.tracks.all())
                except:
                    return "The presentations for your track are not yet planned"
                if t.count() > 0:
                    html = '<p>Your tracks presentations are on:</p><ul>'
                    for p in t:
                        start = timezone.localtime(p.DateTime).strftime("%A %d %B %Y %H:%M")
                        room = p.PresentationRoom
                        html += "<li>"+str(p.Track)+ ": " + str(start) + " in " + str(room) + "</li>"
                    html += "</ul>"
                else:
                    html = "<p>You do not have any presentations to attend</p>"

            else:
                # check if user has presentations, for responsible and assistants that are not trackhead
                try:
                    t = PresentationTimeSlot.objects.filter(Q(Distribution__Proposal__ResponsibleStaff=user) | Q(Distribution__Proposal__Assistants=user))
                except:
                    return "Your presentations are not (yet) planned."
                if t.count() > 0:
                    html = '<p>Your presentations are on:</p><ul>'
                    for p in t:
                        start = timezone.localtime(p.DateTime).strftime("%A %d %B %Y %H:%M")
                        room = p.Presentations.PresentationRoom
                        html += "<li>"+str(start)+" in "+str(room)+"</li>"
                    html += "</ul>"
                else:
                    html = "<p>You do not have any presentations to attend</p>"

            html += '<a href="{}" class ="button primary">{}</a>'
            url = reverse('presentations:presentationscalendar')
            title = "View all presentations"
            st = format_html(html, url, title)
            return st
        else:
            return "Your presentation timeslot will appear here when the planning becomes public."
    except:
        return "Your presentation timeslot will appear here when the planning becomes public."