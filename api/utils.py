#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from proposals.models import Proposal


def getStatStr(status):
    """
    returns string for proposal status change message

    :param status: integer with the status
    :return: a string with the status
    """
    allstatstr = "Proposal status changed to '{}'<br /><ol>".format(Proposal.StatusOptions[status - 1][1])
    for opt in Proposal.StatusOptions:
        allstatstr += "<li class=\""
        if opt[0] == status:
            allstatstr += "text-accent fg-navy"
        else:
            allstatstr += "text-secondary"
        allstatstr += "\">" + opt[1] + "</li>"
    return allstatstr+"</ol>"
