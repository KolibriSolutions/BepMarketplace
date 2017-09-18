from django.core.cache import cache
from django.shortcuts import get_object_or_404

from .models import Proposal


def getProp(pk):
    """
    Get a proposal from cache or from database. Put it in cache if it is not yet in cache.
    
    :param pk: pk of proposal
    :return: 
    """
    cprop = cache.get('proposal_{}'.format(pk))
    if cprop is None:
        prop = get_object_or_404(Proposal, pk=pk)
        if prop.Status == 4:
            cache.set('proposal_{}'.format(pk), prop, None)
        return prop
    else:
        return cprop


def updatePropCache(prop):
    """
    Update a cached proposal
    
    :param prop: proposal object 
    :return: 
    """
    if prop.Status == 4:
        cache.set('proposal_{}'.format(prop.id), prop, None)


def updatePropCache_pk(pk):
    """
    Update a cached proposal
    
    :param pk: pk of proposal
    :return: 
    """
    prop = get_object_or_404(Proposal, pk=pk)
    if prop.Status == 4:
        cache.set('proposal_{}'.format(pk), prop, None)