#  Master Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/MasterMarketplace/blob/master/LICENSE
import logging

from django.core.exceptions import ValidationError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from index.models import UserMeta

logger = logging.getLogger('django')


class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def get_username(self, claims):
        """
        Make a username for new users
        """
        try:
            uid = claims.get('uids')
            if type(uid) == list:
                uid = uid[0]
            return uid.lower()

        except AttributeError:
            raise Exception("Username field (uids) missing from claims")

    def verify_claims(self, claims):
        """
        Check if all information is present in OpenID context

        :param claims:
        :return:
        """
        required_claims = ['uids', 'acr', 'eduperson_affiliation', 'email', 'email_verified', 'schac_home_organization', 'sub', 'updated_at']
        for required_claim in required_claims:
            assert required_claim in claims, f'Claim {required_claim} missing from OpenID claims: {claims}'
        return True

    def update_user(self, user, claims):
        """
        Update information in user info for existing user
        :param user:
        :param claims:
        :return:
        """
        # overwrite if changed
        new_mail = claims.get('email').lower()
        if user.email != new_mail:
            logger.warning(f'Email changed for {user} from {user.email} to {new_mail}')
            user.email = new_mail
            user.save()
        new_uid = self.get_username(claims)
        if user.username != new_uid:
            logger.warning(f'UID changed for {user} from {user.username} to {new_uid}')
            user.username = new_uid
            user.save()
        self.set_user_info(user, claims)
        return user

    def create_user(self, claims):
        """
        Create new user
        :param claims:
        :return:
        """
        email = claims.get('email').lower()
        username = self.get_username(claims)
        user = self.UserModel.objects.create_user(username, email=email)
        self.set_user_info(user, claims)

        return user

    def filter_users_by_claims(self, claims):
        """Return all users matching the specified email or username."""
        assert claims.get('schac_home_organization', None) == 'tue.nl', f"Non-TU/e user trying to login {claims}"

        email = claims.get('email')
        if not email:
            return self.UserModel.objects.none()

        # logger.debug('Trying to find user by email %s', email)
        accounts = self.UserModel.objects.filter(email__iexact=email)
        if accounts.exists():
            return accounts
        else:
            # try username
            accounts = self.UserModel.objects.filter(username__iexact=self.get_username(claims))
            return accounts  # can be none

    def set_user_info(self, user, claims):
        """
        ['uids', 'acr', 'eduperson_affiliation', 'email', 'email_verified',
         'family_name', 'given_name', 'name', 'schac_home_organization',
          'sub', 'updated_at']
        :param user:
        :param claims:
        :return:
        """
        try:
            meta = user.usermeta
        except UserMeta.DoesNotExist:
            meta = UserMeta(User=user)

        # make last name from fullname
        meta.Fullname = claims.get('nickname', None)

        user.last_name = claims.get('family_name', None)
        user.first_name = claims.get('given_name', None)

        meta.Department = claims.get('ou', None)
        meta.Affiliation = claims.get('eduperson_affiliation', None)

        if not meta.Overruled:
            try:
                student_numbers = claims.get('schac_personal_unique_code')[0].split(':')
                meta.Studentnumber = student_numbers[-1][0:19]  # format urn:schac:personalUniqueCode:nl:local:tue.nl;studentid;0803331
            except TypeError:
                pass  # claim can be unavailable
            except Exception as e:
                raise Exception(f'Setting student number failed for {claims}, error {e}')
        try:
            meta.full_clean()
            user.full_clean()
        except ValidationError as e:
            raise Exception(f"Saving updated user {user.email} full_clean failed with {e}")
        user.save()
        meta.save()
