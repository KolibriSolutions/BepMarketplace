#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
from timeline.utils import get_timeslot


def get_all_applications(user, timeslot):
    """
    Get a users applications for this timeslot

    :param user: user to get applications for
    :param timeslot: timeslot to get the applications.
    :return:
    """
    return user.applications.filter(Proposal__TimeSlot=timeslot)