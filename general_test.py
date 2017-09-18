import re
import sys
import traceback
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.test import Client
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils.module_loading import import_module

from general_model import GroupOptions
from index.models import UserMeta
from proposals.models import Proposal
from support.models import Track
from timeline.models import TimeSlot, TimePhase


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
        u.groups.add(self.g2u)
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
        urls = [ x for x in urls if (">" not in x
                                     and "<" not in x
                                     and "//" not in x
                                     and "/static/" not in x
                                     and "/logout/" not in x
                                     and "tracking/live/" not in x
                                     and "tracking/viewnumber/" not in x)]

        for link in urls:  # select the url in href for all a tags(links)
            response2 = self.client.get(link)
            response_code2 = response2.status_code
            self.assertEqual(response_code2, 200,
                             msg='Link to page {} from page {} for user {} returned {} instead of 200'
                             .format(link, sourceurl, user.username, response_code2))
        self.client.logout()

# disable cache for all tests
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class ProposalViewsTest(TestCase):
    """
    Functions to test pages related to proposals
    """
    def setup(self):
        """
        Initialization function for a test. Sets users and other objects to correct settings for testing.

        :return:
        """
        # whether to produce output
        self.debug = False
        # the client used for testing
        self.client = TestClient()
        # Create groups using general_test
        ViewsTest.create_groups(self)
        # create testusers using the naming-patern: [r t]-[s p 1 2 u 3 t ]
        # r=random (any person of the given type), t=this(for this proposal)
        # 1=type1, 2=type2, 3=type3, s=Student, u=Unverified-type2, h=track-Head, p=Private-student
        self.usernames = ['r-3', 'r-s', 't-p', 'r-1', 't-1', 'r-2', 't-2', 't-u', 'r-h', 't-h']
        # Create the users and assign groups/roles.
        self.users = {}
        for n in self.usernames:
            u = User(username=n)
            u.save()
            if n[-1] == '3':
                u.groups.add(self.g3)
            elif n[-1] == '1':
                u.groups.add(self.g1)
            elif n[-1] == '2':
                u.groups.add(self.g2)
            elif n[-1] == 'h':
                u.groups.add(self.g1)
            elif n[-1] == 'u':
                u.groups.add(self.g2u)
            u.save()
            self.users[n] = u
            m = UserMeta(User=u)
            m.save()
        # Track for the proposal, with trackhead t-h
        th = User.objects.get(username='t-h')
        t = Track(Name='Automotive', ShortName='AU', Head=th)
        t.save()
        # Random track head r-h
        rth = User.objects.get(username='r-h')
        rt = Track(Name='Smart Sustainable', ShortName='SSS', Head=rth)
        rt.save()
        # The timeslot used for testing proposal of current timeslot
        self.ts = TimeSlot(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Name='thisyear')
        self.ts.save()
        # The timeslot used for testing proposal of other timeslot
        self.ots = TimeSlot(Begin=datetime.now()-timedelta(days=5), End=datetime.now()-timedelta(days=3), Name='lastyear')
        self.ots.save()
        # The timephase used for testing. The Description is changed every test.
        self.tp = TimePhase(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Timeslot=self.ts, Description=1 )
        self.tp.save()
        # The proposal used for testing
        self.proposal = Proposal(Title="testproposal",
                                 ResponsibleStaff=self.users.get('t-1'),
                                 Group=GroupOptions[0],
                                 NumstudentsMin=1,
                                 NumstudentsMax=1,
                                 GeneralDescription="Test general description",
                                 StudentsTaskDescription="Test student task description",
                                 Status=1,
                                 ECTS=15,
                                 Track=t,
        )

        self.proposal.save()
        self.p = self.proposal.id
        self.proposal.Assistants.add(self.users.get('t-2'))
        self.proposal.Assistants.add(self.users.get('t-u'))
        self.proposal.save()
        # make private proposal
        self.privateproposal = Proposal(Title="privateproposaltest",
                                 ResponsibleStaff=self.users.get('t-1'),
                                 Group=GroupOptions[0],
                                 NumstudentsMin=1,
                                 NumstudentsMax=1,
                                 GeneralDescription="Test general description",
                                 StudentsTaskDescription="Test student task description",
                                 Status=1,
                                 ECTS=15,
                                 Track=t,
        )
        self.privateproposal.save()
        self.ppriv = self.privateproposal.id
        self.privateproposal.Assistants.add(self.users.get('t-2'))
        self.privateproposal.Assistants.add(self.users.get('t-u'))
        self.privateproposal.Private.add(self.users.get('t-p'))
        self.privateproposal.save()

    def loop_user_status(self, view, status, info, kw=None):
        """
        Test all users and proposal status for a given page. Called from self.all_pages_test()

        :param view: name of the page, for reverse view
        :param status: array of http status that is expected for each user
        :param kw: keyword args for the given view.
        :return:
        """
        for username in self.usernames:
            if self.debug:
                print("Testing user {}".format(username))
            info['user'] = username
            info['kw'] = kw
            # log the user in
            u = User.objects.get(username=username)
            self.client.login_user(u)
            # check for each given status from the status-array
            l = len(status)
            for status0 in range(0, l):
                if self.debug:
                    print("Testing status {}".format(self.status))
                self.status = status0 + 1
                info['status'] = self.status
                # Expected response code
                expected = status[status0][self.usernames.index(username)]
                # Reset the proposal status, because it changes after a test call to upgrade/downgrade
                self.proposal.Status = self.status
                self.proposal.save()
                self.privateproposal.Status = self.status
                self.privateproposal.save()
                self.view_test_status(view, expected, info, kw)
            # user logout
            self.client.logout_user(u)

    def view_test_status(self, view, expected, info=None, kw=None):
        """
        Test a given view for a given user with given proposal status (in self.status)

        :param view: a view to test
        :param expected: the expected response code
        :param user: a username of the used user. Only used for debug output
        :param kw: kwargs for the view func
        :return:
        """
        if not info:
            # because default argument is mutable as empty dict.
            info = {}
        try:
            response = self.client.get(reverse(view, kwargs=kw))
            response_code = response.status_code
            if response_code == 403 or expected == 403:
                try:
                    exception = list(response.context[0])[0]["exception"]
                except:
                    try:
                        exception = list(response.context[0])[0]["Message"]
                    except:
                        exception = ''
                info['exception'] = exception
            else:
                info['exception'] = "no 403"
        except Exception as e:
            response_code = 500
            if self.debug:
                print("Error: {}".format(e))
                traceback.print_exc(file=sys.stdout)

        self.assertEqual(response_code, expected,
                         msg='Expected status code {} but got {} for {} info: {}.'
                         .format(expected, response_code, view, info))
