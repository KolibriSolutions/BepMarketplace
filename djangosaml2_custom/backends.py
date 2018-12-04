import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import (
    MultipleObjectsReturned, )
from djangosaml2.backends import Saml2Backend, get_saml_user_model

logger = logging.getLogger('djangosaml2')


def get_user(email, username):
    """
    Find an existing user in the database based on email and username
    Also used in Projects to find users based on email address

    :param email: emailadress to find user with
    :param username: username to find user if email does not match. (if so, triggers warning)
    :return: user account if account exists, None if not exists, MultipleObjectsReturned if email address duplicate user
    """
    try:
        logger.debug('Trying to find user by email %s', email)
        account = get_user_model().objects.get(email__iexact=email)
        return account
    except get_user_model().DoesNotExist:
        # try username
        logger.warning('Email %s login match not succeeded. Trying to find user by username %s', email, username)
        try:
            account = get_user_model().objects.get(username__iexact=username)
            return account
        except get_user_model().DoesNotExist:
            logger.debug('Email not succeeded. Username not succeeded.')
            return None  # user does not exist.
    except MultipleObjectsReturned:
        logger.debug('User has multiple accounts.')
        # user email has a duplicate account with other username.
        raise MultipleObjectsReturned


class Saml2BackendCustom(Saml2Backend):
    """
    Custom backend to be able to match user on both emailadress (default) and username (if email is not matched)
    Simplified implementation of self._get_or_create_saml2_user()
    """
    def get_saml2_user(self, create, main_attribute, attributes, attribute_mapping):
        if not create:
            logger.error('Create unknown user should be enabled for this backend!')
        django_user_main_attribute = self.get_django_user_main_attribute()
        # user_query_args = self.get_user_query_args(main_attribute)  #__iexact is always used
        # user_create_defaults = {django_user_main_attribute: main_attribute}

        # check config and get username + email
        email = attributes['urn:mace:dir:attribute-def:mail'][0]
        if not 'email' == django_user_main_attribute and email == main_attribute:
            logger.error("Please set saml2 MAIN_ATTRIBUTE to 'email'")
        username = attributes['urn:mace:dir:attribute-def:uid'][0]
        logger.debug('Custom Backend: Check if the user "%s" exists or create otherwise',
                     main_attribute)

        # check user by email AND username
        try:
            user = get_user(email, username)
        except MultipleObjectsReturned:
            logger.error("There are more than one user with %s = %s",
                         django_user_main_attribute, main_attribute)
            return None

        if not user:  # user does not yet exist, create it.
            logger.debug('Creating new user')
            user = get_saml_user_model()(
                username=username,
                email=email.lower(),
            )
            logger.debug('New user created')
            user = self.configure_user(user, attributes, attribute_mapping)
        else:  # update existing user
            logger.debug('User updated')
            user = self.update_user(user, attributes, attribute_mapping)
        return user
