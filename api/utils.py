#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from proposals.models import Proposal


def get_status_str(status):
    """
    returns string for proposal status change message

    :param status: integer with the status
    :return: a string with the status
    """
    return "Proposal status changed to '{}'".format(Proposal.StatusOptions[status - 1][1])
