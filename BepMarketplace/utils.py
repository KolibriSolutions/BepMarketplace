#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import (
    MultipleObjectsReturned, )
from django.core.exceptions import PermissionDenied

logger = logging.getLogger('django')


def get_user(email, username):
    """
    Find an existing user in the database based on email and username
    Also used in Projects to find users based on email address
    Needed to map user added by email (for instance by project add assistant by email address) to a user on first login.

    :param email: emailadress to find user with
    :param username: username to find user if email does not match. (if so, triggers warning)
    :return: user account if account exists, None if not exists, MultipleObjectsReturned if email address duplicate user
    """
    try:
        # logger.debug('Trying to find user by email %s', email)
        account = get_user_model().objects.get(email__iexact=email)
        return account
    except get_user_model().DoesNotExist:
        # try username
        # logger.warning('Email %s login match not succeeded. Trying to find user by username %s', email, username)
        try:
            account = get_user_model().objects.get(username__iexact=username)
            return account
        except get_user_model().DoesNotExist:
            # logger.debug('Email not succeeded. Username not succeeded.')
            return None  # user does not exist.
    except MultipleObjectsReturned as e:
        # user email has a duplicate account with other username.
        logger.exception('Login user with multiple accounts: {} - {}'.format(email, username))
        raise PermissionDenied("You have multiple user accounts. Please contact support at {} to get this resolved.".format(settings.CONTACT_EMAIL))
