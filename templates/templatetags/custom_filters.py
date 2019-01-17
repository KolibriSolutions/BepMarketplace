from datetime import datetime

from django import template
from django.db.models import Q
from django.template.defaultfilters import truncatechars
from django.urls.base import reverse
from django.utils import timezone
from django.utils.html import format_html

from general_view import get_grouptype
from proposals.utils import get_all_proposals, can_edit_project_fn, can_downgrade_project_fn
from index.models import Broadcast
from presentations.models import PresentationTimeSlot, PresentationSet, PresentationOptions
from timeline.utils import get_timeslot, get_timephase, get_timephase_number

register = template.Library()


@register.filter(name="index")
def index(lst, i):
    """
    Return a value from a list at index

    :param lst: list
    :param i: index
    :return:
    """
    return lst[int(i)]


@register.filter(name='tolist')
def tolist(object):
    """
    Convert object to list

    :param object:
    :return: list of object
    """
    return list(object)


@register.filter(name='has_group')
def has_group(user, group_names):
    """
    Check groups for given user.

    :param user:
    :param group_names:
    :return:
    """
    if user.is_superuser:
        return True
    if group_names == "any":
        if user.groups.exists():
            if get_grouptype('4') not in user.groups.all() and \
                    get_grouptype('5') not in user.groups.all() and \
                    get_grouptype('6') not in user.groups.all():
                return True
            if user.groups.count() > 1:
                return True
            return False
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
    html = "<a href='" + reverse(
        "proposals:pending") + "'><button class=\"button danger loading-pulse\">Pending: {}</button></a>"
    num = 0

    if get_grouptype("2") in user.groups.all():
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
def GetSlotId():
    """
    Return id of timeslot

    :return:
    """
    ts = get_timeslot()
    if not ts:
        return None
    return ts.pk


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
    if not user.is_authenticated:
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
    if not user.is_authenticated or user.groups.exists():
        return False
    # check if user has distributions
    timeslot = get_timeslot()
    try:
        dist = user.distributions.get(Timeslot=timeslot)
    except:
        return False
    url = reverse('proposals:details', args=[dist.Proposal.pk])
    html = '<p>You are distributed to the proposal:</p><a href="{}" class ="button primary">{}</a></p>'
    title = truncatechars(dist.Proposal.Title, 25)
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


@register.filter(name='can_edit_project')
def can_edit_project_tag(project, user):
    return can_edit_project_fn(user, project, None)[0]


@register.filter(name='can_downgrade_project')
def can_downgrade_project_tag(project, user):
    return can_downgrade_project_fn(user, project)[0]


@register.simple_tag
def GetPresentationStudent(user):
    """
    Displays the presentation for a student

    :param user:
    :return:
    """
    if not user.is_authenticated or user.groups.exists():
        # anonymous or not student
        return False
    ts = get_timeslot()
    try:
        options = ts.presentationoptions
    except PresentationOptions.DoesNotExist:
        return "Your presentation is not yet planned."
    if options.Public or get_timephase_number() == 7:
        # check if user has presentations
        try:
            t = PresentationTimeSlot.objects.get(Q(Distribution__Student=user) &
                                                 Q(Presentations__PresentationOptions__TimeSlot=ts))
        except (PresentationTimeSlot.DoesNotExist, PresentationTimeSlot.MultipleObjectsReturned):
            return "Your presentation is not (yet) planned."
        start = timezone.localtime(t.DateTime).strftime("%A %d %B %Y %H:%M")
        room = t.Presentations.PresentationRoom
        url = reverse('presentations:presentationscalendar')
        title = "View all presentations"
        html = '<p>Your presentation is on {} in {}</p>' \
               '<a href="{}" class ="button primary">{}</a></p>'
        st = format_html(html, start, room, url, title)
        return st
    else:
        return "Your presentation time slot will appear here when the planning becomes public."


@register.simple_tag
def GetPresentationStaff(user):
    """
    Displays the presentation for a staff member
    Only show sets, not individual presentations.

    :param user:
    :return:
    """
    if not user.is_authenticated:
        return False
    # check if not student
    if not user.groups.exists():
        return False
    ts = get_timeslot()
    try:
        options = ts.presentationoptions
    except PresentationOptions.DoesNotExist:
        return "The presentations are not yet planned."  # hide if no options yet.

    if options.Public or get_timephase_number() == 7:
        # check if trackhead has presentations. Show set only.
        html = ''
        if is_trackhead(user):
            try:
                sets = options.presentationsets.filter(Track__in=user.tracks.all())
            except PresentationSet.DoesNotExist:
                return "The presentations for your track are not yet planned"
            if sets.exists():
                html += '<p>Your tracks presentations are starting on:</p><ul>'
                for set in sets:
                    start = timezone.localtime(set.DateTime).strftime("%A %d %B %H:%M")
                    room = set.PresentationRoom
                    html += "<li> {}: {} in {} </li>".format(set.Track, start, room)
                html += "</ul>"
            else:
                html += "<p>You do not have presentations for your track to attend</p>"

        # check if user has presentations, for responsible and assistants. Show each presentation.
        t = PresentationTimeSlot.objects.filter(
            (Q(Distribution__Proposal__ResponsibleStaff=user) | Q(Distribution__Proposal__Assistants=user))
            & Q(Presentations__PresentationOptions=options)).distinct()
        if t.exists():
            html += '<p>Your presentations as supervisor are:</p><ul>'
            for presentation in t:
                start = timezone.localtime(presentation.DateTime).strftime("%A %d %B %H:%M")
                room = presentation.Presentations.PresentationRoom
                html += "<li> {} at {} in {} </li>".format(presentation.Distribution.Student.usermeta.Fullname, start, room)
            html += "</ul>"
        else:
            html += "<p>You do not have any presentations to attend as supervisor.</p>"

        for pset in options.presentationsets.all():
            if user in pset.Assessors.all():  # ugly way to check if a user has to assess anything
                html += '<p>You are assessor for presentations starting on:</p><ul>'
                for set_in in options.presentationsets.all():
                    if user in set_in.Assessors.all():
                        start = timezone.localtime(set_in.DateTime).strftime("%A %d %B %H:%M")
                        room = set_in.PresentationRoom
                        html += "<li>" + str(set_in.Track) + ": " + str(start) + " in " + str(room) + "</li>"
                html += "</ul>"
                break

        html += '<a href="{}" class ="button primary">{}</a>'
        url = reverse('presentations:presentationscalendarown')
        title = "Presentations"
        st = format_html(html, url, title)
        return st
    else:
        return "Your presentation time slot will appear here when the planning becomes public."
