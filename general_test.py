import re

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.module_loading import import_module


class TestClient(Client):
    def init_session(self, session_key):
        """
        Helper function to kill a session

        :param session_key:
        :return:
        """
        engine = import_module(settings.SESSION_ENGINE)
        return engine.SessionStore(session_key)

    def login_user(self, user):
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()

        if self.session:
            request.session = self.session
        else:
            request.session = engine.SessionStore()
        login(request, user)

        # Save the session values.
        request.session.save()

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }

        self.cookies[session_cookie].update(cookie_data)

    def logout_user(self, user):
        for session in Session.objects.all():
            if session.get_decoded().get('_auth_user_id', None) == user.pk:
                request = HttpRequest()
                request.session = self.init_session(session.session_key)
                logout(request)
                break


class ViewsTest(TestCase):
    def setUp(self):
        self.create_groups()
        self.users = {}

        u = User(username='prof0')
        u.save()
        u.groups.add(self.g1)
        u.save()
        self.users['prof0'] = u

        u = User(username='phd0')
        u.save()
        u.groups.add(self.g2)
        u.save()
        self.users['phd0'] = u

        u = User(username='phd1u')
        u.save()
        u.groups.add(self.g2)
        u.save()
        self.users['phd1u'] = u

        u = User(username='suzanne')
        u.save()
        u.groups.add(self.g3)
        u.save()
        self.users['suzanne'] = u

        u = User(username='god')
        u.is_superuser = True
        u.save()
        self.users['god'] = u

        u = User(username='student0')
        u.save()
        self.users['student0'] = u

    def _test_views(self, views):
        client = TestClient()
        for user, user_obj in self.users.items():
            client.login_user(user_obj)
            for view, expected in views.items():
                try:
                    response = client.get(reverse(view))
                    response_code = response.status_code
                except:
                    response_code = 500
                self.assertEqual(response_code, expected[user],
                                msg='Expected status code {} but got {} for {} for user {}'
                                .format(expected[user], response_code, view, user))
            client.logout_user(user_obj)

    def _test_views_args(self, views):
        client = TestClient()
        for user, user_obj in self.users.items():
            client.login_user(user_obj)
            for view, expected in views.items():
                try:
                    response = client.get(reverse(view, args=[1]))
                    response_code = response.status_code
                except:
                    response_code = 500
                self.assertEqual(response_code, expected[user],
                                 msg='Expected status code {} but got {} for {} for user {}'
                                 .format(expected[user], response_code, view, user))
            client.logout_user(user_obj)

    def create_groups(self):
        # setup all groups
        self.g1, self.created = Group.objects.get_or_create(name='type1staff')
        self.g2, self.created = Group.objects.get_or_create(name='type2staff')
        self.g3, self.created = Group.objects.get_or_create(name='type3staff')
        self.g2u, self.created = Group.objects.get_or_create(name='type2staffunverified')
        self.g4, self.created = Group.objects.get_or_create(name='type4staff')
        self.g5, self.created = Group.objects.get_or_create(name='type5staff')
        self.g6, self.created = Group.objects.get_or_create(name='type6staff')


    def links_in_view_test(self, user, sourceurl):
        """
        Find all links in a response and check if they return status 200.

        :param response:
        :return:
        """
        self.client.login_user(user)
        response = self.client.get(sourceurl)
        urls = re.findall('/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+/', str(response.content))
        urls = [ x for x in urls if (">" not in x and "<" not in x and "//" not in x and "/static/" not in x and "/logout/" not in x)]

        for link in urls:  # select the url in href for all a tags(links)
            response2 = self.client.get(link)
            response_code2 = response2.status_code
            self.assertEqual(response_code2, 200,
                             msg='Link to page {} from page {} for user {} returned {} instead of 200'
                             .format(link, sourceurl, user.username, response_code2))
        self.client.logout()
