from django.contrib.auth import get_user_model
from django.core.exceptions import (
    MultipleObjectsReturned, )

def get_user(email, username):
    """
    Find an existing user in the database based on email and username
    Also used in Projects to find users based on email address

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
    except MultipleObjectsReturned:
        # logger.debug('User has multiple accounts.')
        # user email has a duplicate account with other username.
        raise MultipleObjectsReturned