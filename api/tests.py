from django.contrib.auth.models import User
from django.urls import reverse

from general_model import GroupOptions
from general_test import ProposalViewsTest
from index.models import UserMeta


class ApiViewsTest(ProposalViewsTest):
    def setUp(self):
        self.app = 'api'
        super().setUp()

    def test_view_status(self):
        s = self
        # anonymous pages
        codes_anonymous_phase1234567=[
            [['viewsharelink', {'token': 'blabla'}], s.p_allowed]
        ]
        # not related to proposals
        codes_general_phase1234567 = [
            [['verifyassistant', {'pk': 100}], s.p_support],  # use a dummy user without type2staffunverified
            [['getgroupadmins', None], s.p_forbidden],  # god only
            [['getgroupadminsarg', {'group': GroupOptions[0][0]}], s.p_forbidden],
            [['listpublished', None], s.p_allowed],
            [['listpublishedpergroup', None], s.p_allowed],
            [['listpublishedtitles', None], s.p_allowed],
            [['api', None], s.p_allowed],
        ]
        # anonymous proposal pages
        codes_prop_notpublic = [
            [['getpublisheddetail', {'pk': self.p}], s.p_forbidden],
        ]
        codes_prop_public = [
            [['getpublisheddetail', {'pk': self.p}], s.p_allowed],
        ]
        # proposal up/downgrade
        codes_phase1 = [
            [['upgradestatus', {'pk': s.p}],   [s.p_all_this  ,     s.p_no_assistant   , s.p_trackhead    ,   s.p_forbidden]],
            [['downgradestatus', {'pk': s.p}], [s.p_forbidden ,     s.p_all_this       , s.p_no_assistant ,   s.p_trackhead]],
        ]
        codes_phase2 = [
            [['upgradestatus', {'pk': s.p}],   [s.p_all_this  ,     s.p_no_assistant   , s.p_trackhead    ,   s.p_forbidden]],
            [['downgradestatus', {'pk': s.p}], [s.p_forbidden ,     s.p_all_this       , s.p_trackhead    ,   s.p_trackhead]],
        ]
        # TimePhase 3 and later
        codes_phase34567 = [
            [['upgradestatus', {'pk': s.p}],   [s.p_support       , s.p_support         ,s.p_support        , s.p_forbidden]],
            [['downgradestatus', {'pk': s.p}], [s.p_forbidden     , s.p_support         ,s.p_support        , s.p_support  ]],
        ]
        codes_next_ts = [
            [['upgradestatus', {'pk': s.p}],   [s.p_all_this  ,     s.p_no_assistant   , s.p_forbidden    ,   s.p_forbidden]],
            [['downgradestatus', {'pk': s.p}], [s.p_forbidden ,     s.p_all_this       , s.p_no_assistant ,   s.p_trackhead]],
        ]
        codes_prev_ts = [
            [['upgradestatus', {'pk': s.p}],   [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden]],
            [['downgradestatus', {'pk': s.p}], [s.p_forbidden       , s.p_forbidden         ,s.p_forbidden        , s.p_forbidden  ]],
        ]
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes_anonymous_phase1234567:
            self.view_test_status(reverse(self.app+':' + page[0], kwargs=page[1]), 200)
        for page, status in codes_general_phase1234567:
            self.view_test_status(reverse(self.app+':' + page[0], kwargs=page[1]), 302)
        for page, status in codes_prop_notpublic:
            self.view_test_status(reverse(self.app+':' + page[0], kwargs=page[1]), 302)
        for page, status in codes_phase1:
            s.view_test_status(reverse(self.app+':' + page[0], kwargs=page[1]), 302)

        u = User(username='dummy')
        u.id = 100
        u.save()
        m = UserMeta(User=u)
        m.save()

        # Test for users
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1,8), codes_general_phase1234567)
        self.loop_phase_user(range(1,8), codes_prop_notpublic)
        self.loop_phase_user(range(1, 8), codes_anonymous_phase1234567)
        self.proposal.Status = 4
        self.proposal.save()
        self.loop_phase_user(range(1,8), codes_prop_public)

        # proposal up/downgrade
        self.info['type'] = 'proposal phase1'
        self.loop_phase_user([1], codes_phase1)
        # TimePhase 2
        self.info['type'] = 'proposal phase2'
        self.loop_phase_user([2], codes_phase2)
        # TimePhase 3+
        self.info['type'] = 'proposal phase34567'
        self.loop_phase_user([3, 4, 5, 6, 7], codes_phase34567)

        # Test proposal in next timeslot, permissions should be as a proposal in this timeslot in phase 1, except upgrading to status4
        # Change the proposal timeslot to next year
        s.proposal.TimeSlot = s.nts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.nts
        s.privateproposal.save()
        # All phases test with permissions of phase1 of current timeslot.
        self.info['type'] = 'proposal next timeslot'
        self.loop_phase_user(range(1, 8), codes_next_ts)

        # Test proposal in previous timeslot, permissions locked
        # Change the proposal timeslot to next year
        s.proposal.TimeSlot = s.pts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.pts
        s.privateproposal.save()
        # All phases test with permissions of phase1 of current timeslot.
        self.info['type'] = 'proposal previous timeslot'
        self.loop_phase_user(range(1, 8), codes_prev_ts)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")