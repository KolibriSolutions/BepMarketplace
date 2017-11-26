from django.db.models.signals import post_delete
from django.dispatch import receiver
from index.models import UserAcceptedTerms
from django.core.cache import cache

@receiver(post_delete, sender=UserAcceptedTerms)
def clearCacheTerms(sender, **kwargs):
    """
    Clear the cache of users that have accepted the terms.

    :param sender:
    :param kwargs:
    """
    cache.delete('termsaccepted')