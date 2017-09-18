# Create your tests here.

import sys
import traceback
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from general_model import GroupOptions
from general_test import ViewsTest, TestClient
from index.models import UserMeta
from students.models import Application
from support.models import Track
from timeline.models import TimeSlot, TimePhase
from .models import Proposal

# disable cache for all tests
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}})
class ProposalViewsTest(TestCase):
    def setup(self):
        cache.clear()
        self.debug = False
        self.client = TestClient()
        # Create groups
        ViewsTest.create_groups(self)
        # create testusers
        # r=random, a=applied, t=this(for this proposal)
        # s=student, r=responsible, a=assistant, t=trackhead, u=support
        self.usernames = ['r-u', 'r-s', 'r-r', 't-r', 'r-a', 't-a','t-n','r-t','t-t']
        # Create all users as defined in self.usernames of this class.
        self.users = {}
        for n in self.usernames:
            u = User(username=n)
            u.save()
            if n[-1] == 'u':
                u.groups.add(self.g3)
            elif n[-1] == 'r':
                u.groups.add(self.g1)
            elif n[-1] == 'a':
                u.groups.add(self.g2)
            elif n[-1] == 't':
                u.groups.add(self.g1)
            elif n[-1] == 'n':
                u.groups.add(self.g2u)
            u.save()
            self.users[n] = u
            m = UserMeta(User=u)
            m.save()
        # create proposal
        # Track for the proposal, with trackhead t-t
        th = User.objects.get(username='t-t')
        t = Track(Name='Automotive', ShortName='AU', Head=th)
        t.save()
        # Random track head r-t
        rth = User.objects.get(username='r-t')
        rt = Track(Name='Smart Sustainable', ShortName='SSS', Head=rth)
        rt.save()
        # The timeslot used for testing
        self.ts = TimeSlot(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Name='thisyear')
        self.ts.save()
        # The timephase used for testing. The Description is changed every test.
        self.tp = TimePhase(Begin=datetime.now(), End=datetime.now()+timedelta(days=3), Timeslot=self.ts, Description=1 )
        self.tp.save()
        self.proposal = Proposal(Title="testproposal",
                               ResponsibleStaff=self.users.get('t-r'),
                               Group=GroupOptions[0],
                               NumstudentsMin=1,
                               NumstudentsMax=1,
                               GeneralDescription="Test general description",
                               StudentsTaskDescription="Test student task description",
                               Status=1,
                               ECTS=15,
                               Track = t,
        )
        self.proposal.save()
        self.proposal.Assistants.add(self.users.get('t-a'))
        self.proposal.Assistants.add(self.users.get('t-n'))
        self.proposal.save()

    def test_all_views(self):
        """
        Test all views for their http statuscode from the proposals app for a list of usertypes.

        :return:
        """
        # helper functions
        def all_pages_test(page, status):
            """
            Test all cases for a given page for all users.

            :param client: a django testclient
            :param page: the page to test, including arguments.
            :param status: array of http status that is expected for each user
            :return:
            """
            l = len(status)
            for status0 in range(0,l):
                self.status = status0+1
                statusarray = status[status0]
                if self.debug:
                    print("Testing status {}".format(self.status))
                if len(page) == 1:
                    all_users_test(page[0], statusarray, {})
                elif len(page) == 2 and page[1] == 'P':
                    all_users_test(page[0], statusarray, {'pk': self.proposal.id})
                elif len(page) == 3 and page[2] == 'P':
                    for t in page[1]:
                        if self.debug:
                            print("Testing proposal file type {}".format(t))
                        all_users_test(page[0], statusarray, {'pk': self.proposal.id, 'ty': t})

        def all_users_test(view, status, kw={}):
            """
            Test all users for a given page. Called from self.all_pages_test()

            :param view: name of the page, for reverse view
            :param status: array of http status that is expected for each user
            :param kw: keyword args for the given view.
            :return:
            """
            for user in self.usernames:
                u = User.objects.get(username=user)
                expected = status[self.usernames.index(user)]
                self.client.login_user(u)
                self.view_test(view, expected, user, kw)
                self.client.logout_user(u)

        self.setup()
        # expected results:

        # r=random, a=applied, t=this(for this proposal)
        # s=student, r=responsible, a=assistant, n = assistant_not_verified t=trackhead, u=support

        #  usernames = ['r-u', 'r-s', 'r-r', 't-r', 'r-a',   't-a',  't-n',  'r-t',  't-t']
        # different types of permissions
        forbidden =    [403,   403,   403,    403,    403,    403,    403,     403,    403]  # no one
        allowed =      [200,   200,   200,    200,    200,    200,    200,     200,    200]  # everyone
        staff =        [200,   403,   200,    200,    200,    200,    200,     200,    200]  # all staff
        all_this =     [200,   403,   403,    200,    403,    200,    200,     403,    200]  # staff of this proposal
        no_assistant = [200,   403,   403,    200,    403,    403,    403,     403,    200]  # staff of this proposal except assistants
        support =      [200,   403,   403,    403,    403,    403,    403,     403,    403]  # only type3staff (support)
        trackhead =    [200,   403,   403,    403,    403,    403,    403,     403,    200]  # trackhead of proposal, support
        track =        [403,   403,   403,    403,    403,    403,    403,     200,    200]  # any trackhead
        pending =      [403,   403,   200,    200,    200,    200,    200,     200,    200]  # staff with pending proposals
        code_general_phase12345 = [
            [['list'],                       [allowed]],
            [['create'],                     [staff]],
            [['chooseedit'],                 [staff]],
            [['pending'],                    [pending]],
            [['stats'],                      [forbidden]],
            [['statsgeneral'],               [forbidden]],
            [['listtrackproposals'],          [track]]
        ]
        code_general_phase67 =  [
            [['list'],                       [allowed]],
            [['create'],                     [staff]],
            [['chooseedit'],                 [staff]],
            [['pending'],                    [pending]],
            [['stats'],                      [staff]],
            [['statsgeneral'],               [staff]],
            [['listtrackproposals'],          [track]]
        ]

        # These permissions are for a given proposal, which is active in this timeslot (this year).
        #     (1, "Generating project proposals"),
        #     (2, "Projects quality check"),
        #     (3, "Students choosing projects"),
        #     (4, "Distribution of projects"),
        #     (5, "Gather and process objections"),
        #     (6, "Execution of the projects"),
        #     (7, "Presentation of results"),

        # TimePhase 1, generating projects and 2 quality check
        #     Page                            Status 1   Status 2,       Status 3,     Status 4
        code_phase1 = [
            [['addfile',['i','a'],'P'],     [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['editfile',['i','a'],'P'],    [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['edit','P'],                  [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['details','P'],               [ all_this  ,all_this       ,all_this     ,staff       ]],
            [['upgradestatus','P'],         [ all_this  ,no_assistant   ,trackhead    ,forbidden   ]],
            [['downgradestatusmessage','P'],[ forbidden ,all_this       ,no_assistant ,trackhead   ]],
            [['deleteproposal','P'],        [ forbidden ,forbidden      ,forbidden    ,forbidden   ]],
            [['askdeleteproposal','P'],     [ support   ,support        ,forbidden    ,forbidden   ]],
            [['sharelink','P'],             [ all_this  ,all_this       ,trackhead    ,support   ]],
        ]
        code_phase2 = [
            [['addfile',['i','a'],'P'],     [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['editfile',['i','a'],'P'],    [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['edit','P'],                  [ all_this  ,all_this       ,trackhead    ,support     ]],
            [['details','P'],               [ all_this  ,all_this       ,all_this     ,staff    ]],
            [['upgradestatus','P'],         [ all_this  ,no_assistant   ,trackhead    ,forbidden   ]],
            [['downgradestatusmessage','P'],[ forbidden ,all_this       ,trackhead    ,trackhead   ]],
            [['deleteproposal','P'],        [ forbidden ,forbidden      ,forbidden    ,forbidden   ]],
            [['askdeleteproposal','P'],     [ support   ,support        ,forbidden    ,forbidden   ]],
            [['sharelink','P'],             [ all_this  ,all_this       ,trackhead    ,support   ]],
        ]
        # TimePhase 3 and later
        code_phase34567 = [
            [['addfile',['i','a'],'P'],     [ support   ,support        ,support      ,support     ]],
            [['editfile',['i','a'],'P'],    [ support   ,support        ,support      ,support     ]],
            [['edit','P'],                  [ support   ,support        ,support      ,support     ]],
            [['details','P'],               [ all_this  ,all_this       ,all_this     ,allowed     ]],
            [['upgradestatus','P'],         [ support   ,support        ,support      ,forbidden   ]],
            [['downgradestatusmessage','P'],[ forbidden ,support        ,support      ,support     ]],
            [['deleteproposal','P'],        [ forbidden ,forbidden      ,forbidden    ,forbidden   ]],
            [['askdeleteproposal','P'],     [ support   ,support        ,forbidden    ,forbidden   ]],
            [['sharelink','P'],             [ support   ,support        ,support      ,support     ]],
        ]
        self.status = 1
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if self.debug:
            print("not logged in users")
        for page, status in code_general_phase12345:
            self.view_test(page[0], 302)
        for page, status in code_general_phase67:
            self.view_test(page[0], 302)
        for page, status in code_phase1:
            kw = {}
            if len(page) >= 2:
                kw['pk'] = self.proposal.id
                if len(page) == 3:
                    kw['ty'] = 'a'
            self.view_test(page[0], 302, kw=kw)

        # Test general page (not proposal specific)
        if self.debug:
            print("Testing general without stats")
        for phase in range(1,6):
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('General 1, phase {}'.format(phase))
            for page, status in code_general_phase12345:
                all_pages_test(page, status)
        for phase in [6,7]:
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('General 2, phase {}'.format(phase))
            for page, status in code_general_phase67:
                all_pages_test(page, status)

        # Testing proposal specific pages
        # TimePhase 1
        if self.debug:
            print("Testing phase1")
        self.tp.Description = 1
        self.tp.save()
        for page, status in code_phase1:
            all_pages_test(page, status)
        # TimePhase 2
        if self.debug:
            print("Testing phase 2")
        self.tp.Description = 2
        self.tp.save()
        for page, status in code_phase2:
            all_pages_test(page, status)
        # TimePhase 3+
        if self.debug:
            print("Testing phase34567")
        for phase in range(3, 8):
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('Phase {}'.format(phase))
            for page, status in code_phase34567:
                all_pages_test(page, status)

        # Test proposal not in this timeslot, permissions should be as a proposal in this timeslot in phase 1
        # TODO write tests.

    def test_apply_buttons(self):
        """
        Test if the apply/retract buttons show at the right time

        :return:
        """
        self.setup()
        self.proposal.Status = 4
        self.status = 4
        self.proposal.save()
        if self.debug:
            print("Testing apply buttons for student")
        user = User.objects.get(username='r-s')
        self.client.login_user(user)
        view = "proposals:details"

        if self.debug:
            print("Test apply")
        txt = "Apply</button></a>"
        response = self.client.get(reverse(view, kwargs={"pk": self.proposal.id}))
        self.assertContains(response, txt)

        if self.debug:
            print("Test retract")
        a = Application(Student=user, Proposal=self.proposal, Priority=1)
        a.save()
        txt = "Retract Application</button></a>"
        response = self.client.get(reverse(view, kwargs={"pk": self.proposal.id}))
        self.assertContains(response, txt)

        self.client.logout_user(user)

    def test_links_visible(self):
        """
        Test if the visible buttons do return a 200

        :return:
        """
        self.setup()
        self.proposal.Status = 4
        self.status = 4
        self.proposal.save()
        if self.debug:
            print("Testing all links for users")

        view = "proposals:details"

        for username in self.usernames:
            u = User.objects.get(username=username)
            if self.debug:
                print("user {}".format(username))
            ViewsTest.links_in_view_test(self, u, reverse(view, kwargs={"pk": self.proposal.id}))


    def view_test(self, view, expected, user='', kw={}):
        """
        Test a given view for a given user.

        :param view: a view to test
        :param expected: the expected response code
        :param user: a username of the used user.
        :param kw: kwargs for the view func
        :return:
        """

        # Reset the proposal status, because it changes after a test call to upgrade/downgrade
        self.proposal.Status = self.status
        self.proposal.save()
        try:
            view = "proposals:{}".format(view)
            response = self.client.get(reverse(view, kwargs=kw))
            response_code = response.status_code
            if (response_code == 403 or expected == 403) and self.debug:
                try:
                    info = list(response.context[0])[0]["exception"]
                except:
                    try:
                        info = list(response.context[0])[0]["Message"]
                    except:
                        info = ''
                if 'pk' in kw:
                    pk = int(kw['pk'])
                    proj = get_object_or_404(Proposal, pk=pk)
                    print('forbidden for {} with user {} and status {} in timephase {} because {}.'.format(view,
                                                                                                           user,
                                                                                                           proj.Status,
                                                                                                           self.tp.Description,
                                                                                                           info))
                else:
                    print('forbidden for {} with user {} and no proposal because {}.'.format(view, user, info))
        except Exception as e:
            response_code = 500
            if self.debug:
                print("Error: {}".format(e))
            traceback.print_exc(file=sys.stdout)


        self.assertEqual(response_code, expected,
                         msg='Expected status code {} but got {} for {} with user {}.'
                         .format(expected, response_code, view, user))
