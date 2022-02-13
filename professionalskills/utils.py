#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
from general_view import get_grouptype
from presentations.models import PresentationTimeSlot, PresentationSet
from presentations.utils import planning_public
from timeline.utils import get_timeslot


def can_edit_file(user, dist):
    return user == dist.Student and dist.TimeSlot == get_timeslot()


def can_respond_file(user, dist):
    if dist.TimeSlot == get_timeslot():  # current timeslot
        if user in dist.Proposal.Assistants.all() \
                or user == dist.Proposal.ResponsibleStaff \
                or user == dist.Proposal.Track.Head \
                or get_grouptype('3') in user.groups.all():
            return True
    return False


def can_view_files(user, dist):
    if get_grouptype('2u') in user.groups.all():
        return False
    # check permissions
    if get_grouptype('3') in user.groups.all() or \
            get_grouptype('6') in user.groups.all() or \
            user in dist.Proposal.Assistants.all() or \
            user == dist.Proposal.ResponsibleStaff or \
            user == dist.Proposal.Track.Head or \
            user == dist.Student:
        return True
    elif planning_public():
        try:
            if user in dist.presentationtimeslot.Presentations.Assessors.all():
                # assessor can view files
                return True
            else:
                # user is not assessor or planning is not public
                return False
        except (PresentationTimeSlot.DoesNotExist, PresentationSet.DoesNotExist):
            # presentations not yet planned or presentationoptions do not exist.
            return False
    return False
