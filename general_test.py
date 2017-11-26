"""
General functions/classes used in tests.
"""
import re
import re
import sys
import traceback
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.test import TestCase, Client
from django.test import override_settings
from django.urls import reverse
from django.utils.module_loading import import_module

from general_model import GroupOptions
from index.models import UserMeta, UserAcceptedTerms
from proposals.models import Proposal
from support.models import Track, CapacityGroupAdministration
from timeline.models import TimeSlot, TimePhase

# disable cache for all tests
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class ViewsTest(TestCase):
    """
    Class with testclient to test views. Some functions to setup data in the database.
    """

    def setUp(self):
        """
        Setup test data, like users and groups.
        """
        # whether to produce output
        self.debug = False

        # to test that each page is at least tested once, check if all urls of the app are tested.
        urlpatterns = import_module(self.app+'.urls', 'urlpatterns').urlpatterns
        self.allurls = [x.name for x in urlpatterns]

        # the client used for testing
        self.client = Client()
        # info string to show debug info in case of test assertion failure
        self.info = {}
        # Create groups
        self.create_groups()
        self.create_users()

        # The timeslot used for testing proposal of current timeslot
        self.ts = TimeSlot(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Name='thisyear')
        self.ts.save()

        # The timephase used for testing. The Description is changed every test.
        self.tp = TimePhase(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Timeslot=self.ts, Description=1 )
        self.tp.save()

        # Track for automotive, with trackhead t-h. Automotive track must exist because it is special. (distributions)
        th = User.objects.get(username='t-h')
        self.track = Track(Name='Automotive', ShortName='AU', Head=th)
        self.track.save()

        # capacity group administration
        # this capacity group administration
        tcga = CapacityGroupAdministration()
        tcga.Group = GroupOptions[0][0]
        tcga.save()
        tcga.Members.add(User.objects.get(username='t-4'))
        tcga.save()

        # random capacity group administration
        rcga = CapacityGroupAdministration()
        rcga.Group = GroupOptions[1][0]
        rcga.save()
        rcga.Members.add(User.objects.get(username='r-4'))
        rcga.save()

        ## setup matrix with all possible rights
        # expected results:
        # r=random, t=this(for this proposal)
        # s=student, p=private-student, r=responsible, a=assistant, n = assistant_not_verified t=trackhead, u=support
        # matrix with different types of permissions, set for each user of the array self.usernames
        # permissions by user. The order is the order of self.usernames. User 'god' is disabled (not tested).
                #  usernames:  r-1  t-1  r-h  t-h  r-2  t-2  t-u  r-3  r-s  t-p  r-4  t-4  r-5  r-6  god
        self.p_forbidden =    [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403,]  # no one
        self.p_allowed =      [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,]  # everyone

        self.p_staff =        [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 200, 200, 200, 200, 200, ]  # all staff, general
        self.p_staff_prop =   [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 403, 403, 403, 403, 200,]  # all staff, to create proposals
        self.p_staff_stud =   [200, 200, 200, 200, 200, 200, 403, 200, 403, 403, 403, 403, 403, 200, 200,]  # all staff that can see students (1,2,3,6)

        self.p_all_this =     [403, 200, 403, 200, 403, 200, 200, 200, 403, 403, 403, 403, 403, 403, 200,]  # staff of this proposal
        self.p_all_this_dist= [403, 200, 403, 200, 403, 200, 200, 200, 200, 403, 403, 403, 403, 200, 200,]  # staff of this proposal, as distributed to r-s (not t-p!). Also type6 for prv
        self.p_no_assistant = [403, 200, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 200,]  # staff of this proposal except assistants
        self.p_all_this_view =[403, 200, 403, 200, 403, 200, 200, 200, 403, 403, 403, 200, 403, 403, 200,]  # staff of this proposal including view only users (type4)

        self.p_private =      [403, 200, 403, 200, 403, 200, 200, 200, 403, 200, 403, 200, 403, 403, 200,]  # private proposal view status 4
        self.p_trackhead =    [403, 403, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 200,]  # trackhead of proposal and support
        self.p_trackhead_only=[403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200,]  # trackhead of proposal
        self.p_track =        [403, 403, 200, 200, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403,]  # any trackhead
        self.p_pending =      [200, 200, 200, 200, 200, 200, 200, 403, 403, 403, 403, 403, 403, 403, 200,]  # staff with pending proposals

        self.p_support      = [403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 200,]  # type3 support
        self.p_support_prv  = [403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 200, 200,]  # 3+6

        self.p_cgadmin      = [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 200, 403, 403, 200,]  # type4
        self.p_study        = [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 403, 200,]  # type5
        self.p_prv =          [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 200, ]  # 6

        self.p_student =      [403, 403, 403, 403, 403, 403, 403, 403, 200, 200, 403, 403, 403, 403, 200,]  # any student
        self.p_studentnotpriv=[403, 403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 200,]  # student without private proposal

        self.p_404=           [404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404,]  # used to test filesdownload


    def create_groups(self):
        """
        Create all groups for the system.
        """
        self.group_names = [
            'type1staff',  # project responsible
            'type2staff', # project assistant
            'type2staffunverified',  # unverified assistant
            'type3staff',  # support staff
            'type4staff',  # Capacity group administration
            'type5staff',  # Study advisor
            'type6staff',  # Prof skill administration
        ]
        for g in self.group_names:
            group, created = Group.objects.get_or_create(name=g)
            assert created
            # make group object accessable as a class variable. < self.type1staff > etc. 
            setattr(self, g, group)


    def create_users(self):
        """
        Takes self.usernames and creates users based on this. The last character of the username determnines the group
        WARNING: This only generates users and assign groups.
        It does not assign roles (like groupadministration and trackhead models).
        """
        # create testusers using the naming-patern: [r t]-[s p 1 2 u 3 t ]
        # r=random (any person of the given type), t=this(for this proposal)
        # 1=type1, 2=type2, 3=type3, s=Student, u=Unverified-type2, h=track-Head, p=Private-student
        self.usernames = [
            'r-1',  # responsible staff
            't-1',  # responsible staff
            'r-h',  # responsible staff, trackhead
            't-h',  # responsible staff, trackhead
            'r-2',  # assistant
            't-2',  # assistant
            't-u',  # unverified assistant
            'r-3',  # support staff
            'r-s',  # student without private proposal
            't-p',  # student with private proposal
            'r-4',  # Capacity group administration of other group than tested proposal
            't-4',  # Capacity group administration of group of tested proposal
            'r-5',  # Study advisor
            'r-6',  # Prof skill administration
            #'god',  # god user (superuser) # DISABLED, god is too hard to test and not necessary
        ]
        # Create the users and assign groups/roles.
        self.users = {}
        for n in self.usernames:
            u = User(username=n)
            u.save()
            if n[-1] == '1':
                u.groups.add(self.type1staff)
            elif n[-1] == 'h':  # trackhead
                u.groups.add(self.type1staff)
            elif n[-1] == '2':
                u.groups.add(self.type2staff)
            elif n[-1] == 'u':
                u.groups.add(self.type2staffunverified)
            elif n[-1] == '3':
                u.groups.add(self.type3staff)
            elif n[-1] == '4':
                u.groups.add(self.type4staff)
            elif n[-1] == '5':
                u.groups.add(self.type5staff)
            elif n[-1] == '6':
                u.groups.add(self.type6staff)
            elif n == 'god':
                u.is_superuser = True
                u.is_staff = True
            u.save()
            self.users[n] = u
            m = UserMeta(User=u)
            ua = UserAcceptedTerms(User=u)
            ua.save()
            m.save()
            

    def links_in_view_test(self, sourceurl):
        """
        Find all links in a response and check if they return status 200.

        :param sourceurl: the page which is parsed to test the links on the page.
        :return:
        """
        for user in self.users.values():
            if (user.username == 't-u' or user.username == 'r-u') and \
                    self.tp.Description > 3:
                # ignore unverfied assistants in later timephases
                continue
            self.client.force_login(user)
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
                self.info['user'] = user.username
                self.view_test_status(link, 200)
            self.client.logout()

    def loop_phase_user(self, phases, codes):
        """
        Loop over the given phases and test with all codes

        :param phases:
        :param codes:
        :return:
        """
        assert isinstance(phases, list) or isinstance(phases, range)
        for phase in phases:
            self.tp.Description = phase
            self.tp.save()
            self.info['phase'] = str(phase)
            for page, status in codes:
                view = self.app + ":" + page[0]
                if any(isinstance(i, list) for i in status):
                    # we're dealing with proposals status tests here
                    ProposalViewsTest.loop_user_status(self, view, status, page[1])
                else:
                    # normal test without proposals
                    self.loop_user(view, status, page[1])
                # remove the page from the list of urls of this app.
                if page[0] in self.allurls: self.allurls.remove(page[0])

    def loop_user(self, view, status, kw=None):
        """
        Loop over the provided pages with status code for each user and test these.

        :param view: name of the page, for reverse view
        :param status: array of http status that is expected for each user
        :param kw: keyword args for the given view.
        :return:
        """
        for username in self.usernames:
            if self.debug:
                print("Testing user {}".format(username))
            self.info['user'] = username
            self.info['kw'] = kw
            # log the user in
            u = User.objects.get(username=username)
            expected = status[self.usernames.index(username)]
            self.client.force_login(u)
            self.view_test_status(reverse(view, kwargs=kw), expected)
            self.client.logout()

    def view_test_status(self, link, expected):
        """
        Test a given view

        :param self: the instance for the testcase class, containing self.client, the testclient instance.
        :param link: a link to a view to test
        :param expected: the expected response code
        :return:
        """
        try:
            response = self.client.get(link)
            response_code = response.status_code
            if response_code == 403 or expected == 403:
                try:
                    exception = list(response.context[0])[0]["exception"]
                except:
                    try:
                        exception = list(response.context[0])[0]["Message"]
                    except:
                        exception = response.context  # this is a large amount of information
                self.info['exception'] = exception
            else:
                self.info['exception'] = "no 403"
        except Exception as e:
            response_code = 500
            print("Error: {}".format(e))
            self.info['exception'] = '500'
            traceback.print_exc(file=sys.stdout)

        self.assertEqual(response_code, expected,
                         msg='Expected status code {} but got {} for {} info: {}.'
                         .format(expected, response_code, link, self.info))


class ProposalViewsTest(ViewsTest):
    """
    Functions to test pages related to proposals
    """
    def setUp(self):
        """
        Initialization test data. Do not use the testdata from ViewsTest
        """
        # create users and groups in parent function
        super(ProposalViewsTest, self).setUp()

        # Random track head r-h
        rth = User.objects.get(username='r-h')
        rt = Track(Name='Smart Sustainable', ShortName='SSS', Head=rth)
        rt.save()

        # The timeslot used for testing proposal of next timeslot
        self.nts = TimeSlot(Begin=datetime.now()+timedelta(days=5), End=datetime.now()+timedelta(days=8), Name='nextyear')
        self.nts.save()
        # The timeslot used for testing proposal of previous timeslot
        self.pts = TimeSlot(Begin=datetime.now()-timedelta(days=5), End=datetime.now()-timedelta(days=3), Name='prevyear')
        self.pts.save()

        # The proposal used for testing
        self.proposal = Proposal(Title="testproposal",
                                 ResponsibleStaff=self.users.get('t-1'),
                                 Group=GroupOptions[0][0],
                                 NumstudentsMin=1,
                                 NumstudentsMax=1,
                                 GeneralDescription="Test general description",
                                 StudentsTaskDescription="Test student task description",
                                 Status=1,
                                 ECTS=15,
                                 Track=self.track,
                                 TimeSlot=self.ts,
        )

        self.proposal.save()
        self.p = self.proposal.id
        self.proposal.Assistants.add(self.users.get('t-2'))
        self.proposal.Assistants.add(self.users.get('t-u'))
        self.proposal.save()
        # make private proposal
        self.privateproposal = Proposal(Title="privateproposaltest",
                                 ResponsibleStaff=self.users.get('t-1'),
                                 Group=GroupOptions[0][0],
                                 NumstudentsMin=1,
                                 NumstudentsMax=1,
                                 GeneralDescription="Test general description",
                                 StudentsTaskDescription="Test student task description",
                                 Status=1,
                                 ECTS=15,
                                 Track=self.track,
                                TimeSlot=self.ts,
        )
        self.privateproposal.save()
        self.ppriv = self.privateproposal.id
        self.privateproposal.Assistants.add(self.users.get('t-2'))
        self.privateproposal.Assistants.add(self.users.get('t-u'))
        self.privateproposal.Private.add(self.users.get('t-p'))
        self.privateproposal.save()

        print("Private prop id: " + str(self.ppriv) + "; Public prop id:"+str(self.p))

    def loop_user_status(self, view, status, kw=None):
        """
        Test all users and proposal status for a given page. Called from self.all_pages_test()

        :param view: name of the page, for reverse view
        :param status: array of http status that is expected for each user
        :param kw: keyword args for the given view.
        :return:
        """
        assert isinstance(status, list)
        for username in self.usernames:
            if self.debug:
                print("Testing user {}".format(username))
            self.info['user'] = username
            self.info['kw'] = kw
            # log the user in
            u = User.objects.get(username=username)
            #self.client.login_user(u)
            self.client.force_login(u)
            # check for each given status from the status-array
            l = len(status)
            for status0 in range(0, l):
                if self.debug:
                    print("Testing status {}".format(self.status))
                self.status = status0 + 1
                self.info['status'] = self.status
                # Expected response code
                expected = status[status0][self.usernames.index(username)]
                # Reset the proposal status, because it changes after a test call to upgrade/downgrade
                self.proposal.Status = self.status
                self.proposal.save()
                self.privateproposal.Status = self.status
                self.privateproposal.save()
                self.view_test_status(reverse(view, kwargs=kw), expected)
            # user logout
            #self.client.logout_user(u)
            self.client.logout()