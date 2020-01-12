#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django import template
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django.utils.html import format_html

from index.templatetags.index_tags import is_track_head
from presentations.models import PresentationOptions, PresentationTimeSlot, PresentationSet
from timeline.utils import get_timephase_number
from timeline.utils import get_timeslot

register = template.Library()


@register.simple_tag
def get_presentation_student(user):
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
def get_presentations_staff(user):
    """
    Displays the presentations for a staff member
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
        if is_track_head(user):
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
                html += "<li> {} at {} in {} </li>".format(presentation.Distribution.Student.usermeta.get_nice_fullname(), start, room)
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
