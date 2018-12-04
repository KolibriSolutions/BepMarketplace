import logging

from django.contrib.auth.models import User
from django.dispatch import receiver
from djangosaml2.signals import pre_user_save

from index.models import UserMeta

logger = logging.getLogger('djangosaml2')


@receiver(pre_user_save, sender=User)
def custom_update_instance(sender, instance, attributes, user_modified, **kwargs):
    """
    Called in djangsaml2 backend when authenticating.

    :param sender: User class
    :param instance: user object of the logged in user.
    :param attributes: attributes of SAML of the user
    :param user_modified: whether the user is modified
    :param kwargs:
    :return: False, because user is already saved in the function
    """
    logger.debug("Running custom update user on pre_user_save")
    try:
        meta = instance.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta()

    # make last name from fullname
    meta.Fullname = attributes["urn:mace:dir:attribute-def:displayName"][0]
    # re-save email address in lower case
    instance.email = attributes["urn:mace:dir:attribute-def:mail"][0].lower()  # make sure email is lowercase

    # these attributes don't always exist
    try:
        meta.Initials = attributes["Initials"][0]
        instance.last_name = attributes["urn:mace:dir:attribute-def:sn"][0]
        instance.first_name = attributes["urn:mace:dir:attribute-def:givenName"][0]
    except:
        instance.last_name = meta.Fullname

    instance.save()
    instance.usermeta = meta
    instance.save()
    meta.save()
    return False  # User is already saved, so no change
