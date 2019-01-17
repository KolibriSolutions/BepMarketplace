from django.contrib.auth.models import User
from django.urls import reverse

from general_test import ViewsTest, ProjectViewsTestGeneral
from students.models import Application


class ProposalViewsTest(ProjectViewsTestGeneral):
    """
    All tests for proposal views

    """

    def setUp(self):
        self.app = 'proposals'
        super().setUp()

    def test_view_status_general(self):
        s = self

        code_general = [
            [['viewsharelink', {'token': 'blabla'}], [s.p_anonymous]],
            [['stats', None], [s.p_staff12345]],
        ]
        code_general_phase12345 = [
            [['list', None],  s.p_all],
            [['create', None],                     s.p_staff_prop],
            [['chooseedit', None],                 s.p_staff_prop_no4],
            [['pending', None],                    s.p_pending],
            [['statspersonal', None],              s.p_forbidden],  #TODO s.p_staff12345
            [['statsgeneral', None],               s.p_forbidden],  #TODO s.p_staff12345
            [['listtrackproposals', None],         s.p_track],
        ]
        code_general_phase67 = [
            [['list', None], [s.p_all]],
            [['create', None],                     s.p_staff_prop],
            [['chooseedit', None],                 s.p_staff_prop_no4],
            [['pending', None],                    s.p_pending],
            [['statspersonal', None],                      s.p_staff_prop_no4],
            [['statsgeneral', None],               s.p_staff_prop],
            [['listtrackproposals', None],         s.p_track],
        ]

        if s.debug:
            print("Testing general")
        s.status = 1
        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5], code_general_phase12345)
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_general)  # share link
        self.loop_phase_code_user([6, 7], code_general_phase67)


    def test_view_status_nophase(self):
        s = self
        # no phase. Same as "TimePhase 3 and later" but without student rights.
        code_phase_nophase = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_support       , s.p_support         ,s.p_support        , s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view , s.p_all_this_view   ,s.p_all_this_view  , s.p_staff]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view , s.p_all_this_view   ,s.p_all_this_view  , s.p_all_this_view]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_all_this  ]],
            [['upgradestatus', {'pk': s.p}],          [s.p_support       , s.p_support         ,s.p_support        , s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden     , s.p_support         ,s.p_support        , s.p_support  ]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden     , s.p_forbidden       ,s.p_forbidden      , s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support       , s.p_support         ,s.p_forbidden      , s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_all_this  ]],
        ]

        if s.debug:
            print("Testing no phase")
        self.info['type'] = 'proposal no phase'
        self.loop_phase_code_user([-1], code_phase_nophase)

    def test_view_status_ts(self):
        s = self

        code_next_ts = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this       ,     s.p_all_this       , s.p_all_this       ,   s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view  ,     s.p_all_this_view  , s.p_all_this_view  ,   s.p_staff    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view  ,     s.p_all_this_view  , s.p_all_this_view  ,   s.p_all_this_view ]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this       ,     s.p_all_this       , s.p_all_this       ,   s.p_all_this ]],
            [['upgradestatus', {'pk': s.p}],          [s.p_all_this       ,     s.p_no_assistant   , s.p_forbidden      ,   s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden      ,     s.p_all_this       , s.p_no_assistant   ,   s.p_trackhead]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden      ,     s.p_forbidden      , s.p_forbidden      ,   s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support        ,     s.p_support        , s.p_forbidden      ,   s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_all_this       ,     s.p_all_this       , s.p_all_this       ,   s.p_all_this  ]],
        ]
        code_prev_ts = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['edit', {'pk': s.p}],                   [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this        , s.p_all_this          ,s.p_all_this         , s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view   , s.p_all_this_view     ,s.p_all_this_view    , s.p_staff ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view   , s.p_all_this_view     ,s.p_all_this_view    , s.p_all_this_view  ]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this        , s.p_all_this          ,s.p_all_this         , s.p_all_this  ]],
            [['upgradestatus', {'pk': s.p}],          [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support         , s.p_support           ,s.p_forbidden        , s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
        ]

        if s.debug:
            print("Testing next ts")
        # Test proposal in next timeslot, permissions should be as a proposal in this timeslot in phase 1, except upgrading to status4
        # Change the proposal timeslot to next year
        s.proposal.TimeSlot = s.nts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.nts
        s.privateproposal.save()
        # All phases test with permissions of phase1 of current timeslot.
        self.info['type'] = 'proposal next timeslot'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_next_ts)

        if s.debug:
            print("Testing prev ts")
        # Test proposal in previous timeslot, permissions locked
        # Change the proposal timeslot to next year
        s.proposal.TimeSlot = s.pts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.pts
        s.privateproposal.save()
        # All phases test with permissions of phase1 of current timeslot.
        self.info['type'] = 'proposal previous timeslot'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_prev_ts)


    def test_view_status_phases(self):
        """
        Test all views for their http statuscode from the proposals app for a list of usertypes.
        Tests for each page each:
        - timephase
        - proposal status
        - user (as defined in self.setup()

        :return:
        """
        s = self


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
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_all_this      ,     s.p_all_this       , s.p_trackhead     ,   s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_all_this      ,     s.p_all_this       , s.p_trackhead     ,   s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_all_this      ,     s.p_all_this       , s.p_trackhead     ,   s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_all_this      ,     s.p_all_this       , s.p_trackhead     ,   s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_all_this      ,     s.p_all_this       , s.p_trackhead     ,   s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this      ,     s.p_all_this       , s.p_all_this      ,   s.p_staff_prop    ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view ,     s.p_all_this_view  , s.p_all_this_view ,   s.p_staff    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view ,     s.p_all_this_view  , s.p_all_this_view ,   s.p_all_this_view ]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this      ,     s.p_all_this       , s.p_all_this      ,   s.p_all_this ]],
            [['upgradestatus', {'pk': s.p}],          [s.p_all_this      ,     s.p_no_assistant   , s.p_trackhead     ,   s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden     ,     s.p_all_this       , s.p_no_assistant  ,   s.p_no_assistant]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden     ,     s.p_forbidden      , s.p_forbidden     ,   s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support       ,     s.p_support        , s.p_forbidden     ,   s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_all_this      ,     s.p_all_this       , s.p_all_this      ,   s.p_all_this  ]],
        ]
        code_phase2 = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_all_this         ,     s.p_all_this       , s.p_trackhead        ,   s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_all_this         ,     s.p_all_this       , s.p_trackhead        ,   s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_all_this         ,     s.p_all_this       , s.p_trackhead        ,   s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_all_this         ,     s.p_all_this       , s.p_trackhead        ,   s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_all_this         ,     s.p_all_this       , s.p_trackhead        ,   s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this         ,     s.p_all_this       , s.p_all_this         ,   s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view    ,     s.p_all_this_view  , s.p_all_this_view    ,   s.p_staff    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view    ,     s.p_all_this_view  , s.p_all_this_view    ,   s.p_all_this_view ]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this         ,     s.p_all_this       , s.p_all_this         ,   s.p_all_this ]],
            [['upgradestatus', {'pk': s.p}],          [s.p_all_this         ,     s.p_no_assistant   , s.p_trackhead        ,   s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden        ,     s.p_all_this       , s.p_trackhead        ,   s.p_trackhead]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden        ,     s.p_forbidden      , s.p_forbidden        ,   s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support          ,     s.p_support        , s.p_forbidden        ,   s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_all_this         ,     s.p_all_this       , s.p_all_this         ,   s.p_all_this  ]],
        ]
        # TimePhase 3 and later, except proposaldetails for private proposal.
        code_phase34567 = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_support       , s.p_support         ,s.p_support        , s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view , s.p_all_this_view   ,s.p_all_this_view  , s.p_all]],
            [['upgradestatus', {'pk': s.p}],          [s.p_support       , s.p_support         ,s.p_support        , s.p_forbidden]],
            [['downgradestatusmessage', {'pk': s.p}], [s.p_forbidden     , s.p_support         ,s.p_support        , s.p_support  ]],
            [['deleteproposal', {'pk': s.p}],         [s.p_forbidden     , s.p_forbidden       ,s.p_forbidden      , s.p_forbidden]],
            [['askdeleteproposal', {'pk': s.p}],      [s.p_support       , s.p_support         ,s.p_forbidden      , s.p_forbidden]],
            [['sharelink', {'pk': s.p}],              [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_all_this  ]],
        ]
        # checks for proposal private details in phase 3456 and 7 seperate. Because assessor can view private proposal in phase 7.
        code_phase3456 = [
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view, s.p_all_this_view,   s.p_all_this_view,    s.p_private]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this,      s.p_all_this,        s.p_all_this,         s.p_all_this]],

        ]
        code_phase7 = [
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view, s.p_all_this_view,   s.p_all_this_view,    s.p_private_pres]],
            [['copy', {'pk': s.ppriv}],               [s.p_all_this,      s.p_all_this,        s.p_all_this,         s.p_all_this_pres]],

        ]


        # Testing proposal specific pages

        # TimePhase 1
        if s.debug:
            print("Testing phase1")
        self.info['type'] = 'proposal phase1'
        self.loop_phase_code_user([1], code_phase1)
        # TimePhase 2
        if s.debug:
            print("Testing phase2")
        self.info['type'] = 'proposal phase2'
        self.loop_phase_code_user([2], code_phase2)

        # TimePhase 3+
        if s.debug:
            print("Testing phase3+")
        self.info['type'] = 'proposal phase34567'
        self.loop_phase_code_user([3, 4, 5, 6, 7], code_phase34567)
        if s.debug:
            print("Testing phase 3+ private")
        self.info['type'] = 'proposal details private phase3456'
        self.loop_phase_code_user([3, 4, 5, 6], code_phase3456)
        self.info['type'] = 'proposal details private phase7'
        self.loop_phase_code_user([7], code_phase7)

    # def test_edit_form(self): #TODO: test if the correct form is shown with self.client.post to a field allowed
    #                                   in the full form but not in the shorter

    # def test_check_url_coverage(self):
    #     # make sure all urls of this app are tested.
    #     self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    def test_apply_buttons(s):
        """
        Test if the apply/retract buttons show at the right time

        :return:
        """
        s.status = 4
        s.proposal.Status = 4
        s.privateproposal.Status = 4
        s.privateproposal.save()
        s.proposal.save()
        s.tp.Description = 3
        s.tp.save()
        if s.debug:
            print("Testing apply buttons for student")

        user = User.objects.get(username='r-s')
        s.client.force_login(user)
        view = "proposals:details"

        if s.debug:
            print("Test apply")
        txta = "Apply</a>"
        response = s.client.get(reverse(view, kwargs={"pk": s.p}))
        s.assertContains(response, txta)

        if s.debug:
            print("Test retract")
        a = Application(Student=user, Proposal=s.proposal, Priority=1)
        a.save()
        txtr = "Retract Application</a>"
        response = s.client.get(reverse(view, kwargs={"pk": s.p}))
        s.assertContains(response, txtr)

        if s.debug:
            print("Test private")
        s.client.logout()
        user = User.objects.get(username='t-p')
        s.client.force_login(user)
        response = s.client.get(reverse(view, kwargs={"pk": s.ppriv}))
        s.assertNotContains(response, txta)
        s.assertNotContains(response, txtr)
        s.client.logout()

    def test_links_visible(s):
        """
        Test if the visible buttons do return a 200

        :return:
        """
        s.proposal.Status = 4
        s.privateproposal.Status = 4
        s.status = 4
        s.proposal.save()
        s.privateproposal.save()

        # only test last timephase
        s.tp.Description = 7
        s.tp.save()

        # assistants will all be verified
        s.usernames.remove('t-u')

        if s.debug:
            print("Testing all links for users")

        view = "proposals:details"

        ViewsTest.links_in_view_test(s, reverse(view, kwargs={"pk": s.proposal.id}))
