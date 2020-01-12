#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.core.cache import cache
from django.db.models.signals import post_delete
from django.dispatch import receiver

from index.models import UserAcceptedTerms


@receiver(post_delete, sender=UserAcceptedTerms)  # call after any 'acceptedterms' object is deleted.
def clear_cache_terms(sender, **kwargs):
    """
    Clear the cache of users that have accepted the terms.

    :param sender:
    :param kwargs:
    """
    cache.delete('termsaccepted')
