#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User
from django.urls import reverse

from general_test import ViewsTest, ProjectViewsTestGeneral
from students.models import Application
from .urls import general_urlpatterns, status_urlpatterns


class ProposalViewsTest(ProjectViewsTestGeneral):
    """
    All tests for proposal views

    """

    def setUp(self):
        self.app = 'proposals'
        super().setUp()

    def test_view_status_general(self):
        s = self
        self.allurls = [x.name for x in general_urlpatterns]

        code_general = [
            [['viewsharelink', {'token': 'blabla'}], [s.p_anonymous]],
            [['stats', None], [s.p_staff_veri]],
            [['exports', None], self.p_support],
            [['contentpolicy', None], self.p_support],
            [['contentpolicycalc', None], self.p_support],
            [['privateproposals', None], self.p_support_prv],
            [['privateproposals', {'timeslot': self.ts.pk}], self.p_support_prv],
            [['listgroupproposals', None], self.p_cgadmin],
            [['listgroupproposals', {'timeslot': self.ts.pk}], self.p_cgadmin],
            [['chooseedit', None], s.p_staff122u35],
            [['chooseedit', {'timeslot': self.ts.pk}], s.p_staff122u35],
            [['list_old', None], s.p_redirect],
            [['list', None], s.p_all],
            [['list', {'timeslot': self.ts.pk}], s.p_all],
            [['list', {'timeslot': self.nts.pk}], s.p_all],
            [['list', {'timeslot': self.pts.pk}], s.p_forbidden],
            # [['favorites', None], s.p_all],
            [['create', None], s.p_staff_prop],
            [['pending', None], s.p_pending],
            [['listtrackproposals', None], s.p_track],
        ]
        code_general_phase1234 = [
            [['statspersonal', {'timeslot': self.ts.pk}], s.p_forbidden],
            [['statspersonal', {'timeslot': self.ts.pk, 'step': 0}], s.p_forbidden],
            [['statspersonal', {'timeslot': self.ts.pk, 'step': 1}], s.p_forbidden],
        ]
            # [['statspersonal', None],              s.p_forbidden],
            # [['statsgeneral', None],               s.p_forbidden],
        # ]
        code_general_phase567 = [

            [['statspersonal', {'timeslot': self.ts.pk}], s.p_staff_prop_nou],
            [['statspersonal', {'timeslot': self.ts.pk, 'step': 0}], s.p_staff_prop_nou],
            [['statspersonal', {'timeslot': self.ts.pk, 'step': 1}], s.p_staff_prop_nou],
        ]
            # [['statspersonal', None],              s.p_staff_prop_nou],
            # [['statsgeneral', None],               s.p_staff_veri],
        # ]

        if s.debug:
            print("Testing general")
        s.status = 1
        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2, 3, 4], code_general_phase1234)
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_general)  # share link
        self.loop_phase_code_user([5, 6, 7], code_general_phase567)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    def test_view_status_nophase(self):
        self.allurls = [x.name for x in status_urlpatterns]

        s = self
        # no phase. Same as "TimePhase 3 and later" but without student rights.
        code_phase_nophase = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_support       , s.p_support         ,s.p_support        , s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_support       , s.p_support         ,s.p_support        , s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this      , s.p_all_this        ,s.p_all_this       , s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view , s.p_all_this_view   ,s.p_all_this_view  , s.p_all]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view , s.p_all_this_view   ,s.p_all_this_view  , s.p_private]],
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

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    def test_view_status_ts(self):
        self.allurls = [x.name for x in status_urlpatterns]
        s = self

        code_next_ts = [
            [['addfile', {'ty': 'i', 'pk': s.p}],     [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['addfile', {'ty': 'a', 'pk': s.p}],     [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['editfile', {'ty': 'i', 'pk': s.p}],    [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['editfile', {'ty': 'a', 'pk': s.p}],    [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_support  ]],
            [['edit', {'pk': s.p}],                   [s.p_all_this       ,     s.p_all_this       , s.p_trackhead      ,   s.p_no_assistant  ]],
            [['copy', {'pk': s.p}],                   [s.p_all_this       ,     s.p_all_this       , s.p_all_this       ,   s.p_staff_prop  ]],
            [['details', {'pk': s.p}],                [s.p_all_this_view  ,     s.p_all_this_view  , s.p_all_this_view  ,   s.p_all    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view  ,     s.p_all_this_view  , s.p_all_this_view  ,   s.p_private]],
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
            [['sharelink', {'pk': s.p}],              [s.p_all_this       , s.p_all_this         ,s.p_all_this        , s.p_all_this  ]],
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

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    def test_view_status_phases(self):
        """
        Test all views for their http statuscode from the proposals app for a list of usertypes.
        Tests for each page each:
        - timephase
        - proposal status
        - user (as defined in self.setup()

        :return:
        """
        self.allurls = [x.name for x in status_urlpatterns]
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
            [['details', {'pk': s.p}],                [s.p_all_this_view ,     s.p_all_this_view  , s.p_all_this_view ,   s.p_all    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view ,     s.p_all_this_view  , s.p_all_this_view ,   s.p_private ]],
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
            [['details', {'pk': s.p}],                [s.p_all_this_view    ,     s.p_all_this_view  , s.p_all_this_view    ,   s.p_all    ]],
            [['details', {'pk': s.ppriv}],            [s.p_all_this_view    ,     s.p_all_this_view  , s.p_all_this_view    ,   s.p_private ]],
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

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    # def test_edit_form(self): #TODO: test if the correct form is shown with self.client.post to a field allowed
    #                                   in the full form but not in the shorter

    # def test_check_url_coverage(self):
    #     # make sure all urls of this app are tested.
    #     self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

    def test_apply_buttons(self):
        """
        Test if the apply/retract buttons show at the right time

        :return:
        """
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
        self.client.force_login(user)
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
        self.client.logout()
        user = User.objects.get(username='t-p')
        self.client.force_login(user)
        response = self.client.get(reverse(view, kwargs={"pk": self.ppriv}))
        self.assertNotContains(response, txta)
        self.assertNotContains(response, txtr)
        self.client.logout()

    def test_links_visible(self):
        """
        Test if the visible buttons do return a 200

        :return:
        """

        # only test last timephase
        self.tp.Description = 7
        self.tp.save()

        # assistants will all be verified
        self.usernames.remove('t-u')
        if self.debug:
            print("Testing all links for users")

        view = "proposals:details"

        ViewsTest.links_in_view_test(self, reverse(view, kwargs={"pk": self.proposal.id}))
