#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache

from tracking.models import ProposalTracking


def get_project_tracking(proposal):
    """
    try retrieving the object from cache, if not in cache from db, if not in db, create it. update cache accordingly

    :param proposal:
    :return:
    """
    c_track = cache.get('trackprop{}'.format(proposal.id))
    if c_track is None:
        try:
            track = ProposalTracking.objects.get(Subject=proposal)
        except ProposalTracking.DoesNotExist:
            track = ProposalTracking()
            track.Subject = proposal
            track.save()
        cache.set('trackprop{}'.format(proposal.id), track, None)
        return track
    else:
        return c_track


def tracking_visit_project(project, user):
    """
    Add a proposal-visit to the list of visitors to count unique student views to a proposal

    :param project: the proposal
    :param user: the visiting user.
    :return:
    """
    # only for students
    if user.groups.exists() or user.is_superuser:
        return

    # only for published
    if project.Status != 4:
        return

    # retrieve object
    track = get_project_tracking(project)

    # add if it is unique visitor and write to both db and cache
    if user not in track.UniqueVisitors.all():
        track.UniqueVisitors.add(user)
        track.save()
        cache.set('trackprop{}'.format(project.id), track, None)

        # notify listeners
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('viewnumber{}'.format(project.id), {
            'type': 'update',
            'text': str(track.UniqueVisitors.count()),
        })
