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
