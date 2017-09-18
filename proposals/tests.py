# Create your tests here.

from django.contrib.auth.models import User

from django.urls import reverse

from general_test import ViewsTest, ProposalViewsTest
from students.models import Application
from students.models import Distribution
from .models import Proposal


class ProposalViewsTest(ProposalViewsTest):
    """
    All tests for proposal views

    """
    def test_view_status(self):
        """
        Test all views for their http statuscode from the proposals app for a list of usertypes.
        Tests for each page each:
        - timephase
        - proposal status
        - user (as defined in self.setup()

        :return:
        """

        # setup environment
        self.setup()
        app = 'proposals:'
        # expected results:
        # r=random, t=this(for this proposal)
        # s=student, p=private-student, r=responsible, a=assistant, n = assistant_not_verified t=trackhead, u=support
        # matrix with different types of permissions, set for each user of the array self.usernames

        #  usernames = ['r-3', 'r-s' 't-p', 'r-1', 't-1', 'r-2',   't-2',  't-u',  'r-h',  't-h']
        forbidden =    [403,   403,   403,   403,    403,    403,    403,    403,     403,    403]  # no one
        allowed =      [200,   200,   200,   200,    200,    200,    200,    200,     200,    200]  # everyone
        private =      [200,   403,   200,   403,    200,    403,    200,    200,     403,    200]  # private proposal view status 4
        staff =        [200,   403,   403,   200,    200,    200,    200,    200,     200,    200]  # all staff
        all_this =     [200,   403,   403,   403,    200,    403,    200,    200,     403,    200]  # staff of this proposal
        no_assistant = [200,   403,   403,   403,    200,    403,    403,    403,     403,    200]  # staff of this proposal except assistants
        support =      [200,   403,   403,   403,    403,    403,    403,    403,     403,    403]  # only type3staff (support)
        trackhead =    [200,   403,   403,   403,    403,    403,    403,    403,     403,    200]  # trackhead of proposal, support
        track =        [403,   403,   403,   403,    403,    403,    403,    403,     200,    200]  # any trackhead
        pending =      [403,   403,   403,   200,    200,    200,    200,    200,     200,    200]  # staff with pending proposals

        # Use the above-defined matrix of permissions to set permissions for some pages.
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
        # reverse name of page to test, and the kw.       Status 1        Status 2,        Status 3,        Status 4
        code_phase1 = [
            [['addfile', {'ty': 'i', 'pk': self.p}],     [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['addfile', {'ty': 'a', 'pk': self.p}],     [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['editfile', {'ty': 'i', 'pk': self.p}],    [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['editfile', {'ty': 'a', 'pk': self.p}],    [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['edit', {'pk': self.p}],                   [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['details', {'pk': self.p}],                [all_this  ,     all_this       , all_this     ,   staff    ]],
            [['details', {'pk': self.ppriv}],            [all_this  ,     all_this       , all_this     ,   all_this ]],
            [['upgradestatus', {'pk': self.p}],          [all_this  ,     no_assistant   , trackhead    ,   forbidden]],
            [['downgradestatusmessage', {'pk': self.p}], [forbidden ,     all_this       , no_assistant ,   trackhead]],
            [['deleteproposal', {'pk': self.p}],         [forbidden ,     forbidden      , forbidden    ,   forbidden]],
            [['askdeleteproposal', {'pk': self.p}],      [support   ,     support        , forbidden    ,   forbidden]],
            [['sharelink', {'pk': self.p}],              [all_this  ,     all_this       , trackhead    ,   support  ]],
        ]
        code_phase2 = [
            [['addfile', {'ty': 'i', 'pk': self.p}],     [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['addfile', {'ty': 'a', 'pk': self.p}],     [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['editfile', {'ty': 'i', 'pk': self.p}],    [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['editfile', {'ty': 'a', 'pk': self.p}],    [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['edit', {'pk': self.p}],                   [all_this  ,     all_this       , trackhead    ,   support  ]],
            [['details', {'pk': self.p}],                [all_this  ,     all_this       , all_this     ,   staff    ]],
            [['details', {'pk': self.ppriv}],            [all_this  ,     all_this       , all_this     ,   all_this ]],
            [['upgradestatus', {'pk': self.p}],          [all_this  ,     no_assistant   , trackhead    ,   forbidden]],
            [['downgradestatusmessage', {'pk': self.p}], [forbidden ,     all_this       , trackhead    ,   trackhead]],
            [['deleteproposal', {'pk': self.p}],         [forbidden ,     forbidden      , forbidden    ,   forbidden]],
            [['askdeleteproposal', {'pk': self.p}],      [support   ,     support        , forbidden    ,   forbidden]],
            [['sharelink', {'pk': self.p}],              [all_this  ,     all_this       , trackhead    ,   support  ]],
        ]
        # TimePhase 3 and later
        code_phase34567 = [
            [['addfile', {'ty': 'i', 'pk': self.p}],     [support       , support         ,support        , support  ]],
            [['addfile', {'ty': 'a', 'pk': self.p}],     [support       , support         ,support        , support  ]],
            [['editfile', {'ty': 'i', 'pk': self.p}],    [support       , support         ,support        , support  ]],
            [['editfile', {'ty': 'a', 'pk': self.p}],    [support       , support         ,support        , support  ]],
            [['edit', {'pk': self.p}],                   [support       , support         ,support        , support  ]],
            [['details', {'pk': self.p}],                [all_this      , all_this        ,all_this       , allowed  ]],
            [['details', {'pk': self.ppriv}],            [all_this      , all_this        ,all_this       , private  ]],
            [['upgradestatus', {'pk': self.p}],          [support       , support         ,support        , forbidden]],
            [['downgradestatusmessage', {'pk': self.p}], [forbidden     , support         ,support        , support  ]],
            [['deleteproposal', {'pk': self.p}],         [forbidden     , forbidden       ,forbidden      , forbidden]],
            [['askdeleteproposal', {'pk': self.p}],      [support       , support         ,forbidden      , forbidden]],
            [['sharelink', {'pk': self.p}],              [support       , support         ,support        , support  ]],
        ]
        self.status = 1
        # info object with debug info if assertion fails
        info = {}
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if self.debug:
            print("not logged in users")
        info['type'] = 'not logged in'
        for page, status in code_general_phase12345:
            self.view_test_status(app+page[0], 302)
        for page, status in code_general_phase67:
            self.view_test_status(app+page[0], 302)
        for page, status in code_phase1:
            self.view_test_status(app+page[0], 302, kw=page[1])

        # Test general page (not proposal specific)
        if self.debug:
            print("Testing general without stats")
        info['type'] = 'general'
        for phase in range(1, 6):
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('General 1, phase {}'.format(phase))
            info['phase'] = str(phase)
            for page, status in code_general_phase12345:
                self.loop_user_status(app+page[0], status, info)
        for phase in [6, 7]:
            self.tp.Description = phase
            self.tp.save()
            info['phase'] = str(phase)
            if self.debug:
                print('General 2, phase {}'.format(phase))
            for page, status in code_general_phase67:
                self.loop_user_status(app+page[0], status, info)

        # Testing proposal specific pages
        # TimePhase 1
        if self.debug:
            print("Testing phase1")
        info['type'] = 'proposal phase1'
        self.tp.Description = 1
        self.tp.save()
        info['phase'] = str(1)
        for page, status in code_phase1:
            self.loop_user_status(app+page[0], status, info, page[1])

        # TimePhase 2
        if self.debug:
            print("Testing phase 2")
        info['type'] = 'proposal phase2'
        self.tp.Description = 2
        self.tp.save()
        info['phase'] = str(2)
        for page, status in code_phase2:
            self.loop_user_status(app+page[0], status, info, page[1])
        # TimePhase 3+
        info['type'] = 'proposal phase3+'
        if self.debug:
            print("Testing phase34567")
        for phase in range(3, 8):
            self.tp.Description = phase
            self.tp.save()
            info['phase'] = str(phase)
            if self.debug:
                print('Phase {}'.format(phase))
            for page, status in code_phase34567:
                self.loop_user_status(app+page[0], status, info, page[1])

        # Test proposal not in this timeslot, permissions should be as a proposal in this timeslot in phase 1
        # Change the proposal timeslot to last year
        self.proposal.TimeSlot = self.ots
        self.proposal.save()
        self.privateproposal.TimeSlot = self.ots
        self.privateproposal.save()
        # All phases test with permissions of phase1 of current timeslot.
        if self.debug:
            print("Testing all phases for other timeslot")
        info['type'] = 'proposal other timeslot'
        self.tp.Description = 1
        self.tp.save()
        for phase in range(1, 8):
            self.tp.Description = phase
            self.tp.save()
            info['phase'] = str(phase)
            for page, status in code_phase1:
                self.loop_user_status(app+page[0], status, info, page[1])


    def test_apply_buttons(self):
        """
        Test if the apply/retract buttons show at the right time

        :return:
        """
        self.setup()
        self.status = 4
        self.proposal.Status = 4
        self.privateproposal.Status = 4
        self.privateproposal.save()
        self.proposal.save()
        self.tp.Description = 3
        self.tp.save()
        if self.debug:
            print("Testing apply buttons for student")

        user = User.objects.get(username='r-s')
        self.client.login_user(user)
        view = "proposals:details"

        if self.debug:
            print("Test apply")
        txta = "Apply</a>"
        response = self.client.get(reverse(view, kwargs={"pk": self.p}))
        self.assertContains(response, txta)

        if self.debug:
            print("Test retract")
        a = Application(Student=user, Proposal=self.proposal, Priority=1)
        a.save()
        txtr = "Retract Application</a>"
        response = self.client.get(reverse(view, kwargs={"pk": self.p}))
        self.assertContains(response, txtr)

        if self.debug:
            print("Test private")
        self.client.logout_user(user)
        user = User.objects.get(username='t-p')
        self.client.login_user(user)
        response = self.client.get(reverse(view, kwargs={"pk": self.ppriv}))
        self.assertNotContains(response, txta)
        self.assertNotContains(response, txtr)
        self.client.logout_user(user)

    def test_links_visible(self):
        """
        Test if the visible buttons do return a 200

        :return:
        """
        self.setup()
        self.proposal.Status = 4
        self.privateproposal.Status = 4
        self.status = 4
        self.proposal.save()
        self.privateproposal.save()

        # only test last timephase
        self.tp.Description = 7
        self.tp.save()

        # assistants will all be verified
        self.usernames.remove('t-u')

        # Distribute the student, such that professionalskills files becomes available.
        d = Distribution(Proposal=Proposal.objects.get(id=1), Student=self.users.get('r-s'), Timeslot=self.ts)
        d.save()
        dp = Distribution(Proposal=Proposal.objects.get(id=2), Student=self.users.get('t-p'), Timeslot=self.ts)
        dp.save()
        if self.debug:
            print("Testing all links for users")

        view = "proposals:details"

        for username in self.usernames:
            u = User.objects.get(username=username)
            if self.debug:
                print("user {}".format(username))
            ViewsTest.links_in_view_test(self, u, reverse(view, kwargs={"pk": self.proposal.id}))
