from django.contrib.auth.models import User
from django.urls import reverse

from general_model import GroupOptions
from general_test import ProjectViewsTestGeneral
from index.models import UserMeta


class ApiViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'api'
        super().setUp()

        self.dummy = User(username='dummy')
        self.dummy.save()
        m = UserMeta(User=self.dummy)
        m.save()

    def test_view_status(self):
        s = self
        # not related to proposals
        codes_general_phase1234567 = [
            [['verifyassistant', {'pk': self.dummy.id}], s.p_support],  # use a dummy user without type2staffunverified
            [['getgroupadmins', None], s.p_superuser],  # god only
            [['getgroupadminsarg', {'group': GroupOptions[0][0]}], s.p_superuser],
            [['listpublished', None], s.p_all],
            [['listpublishedpergroup', None], s.p_all],
            [['listpublishedtitles', None], s.p_all],
            [['api', None], s.p_all],
        ]
        # anonymous proposal pages
        codes_prop_notpublic = [
            [['getpublisheddetail', {'pk': self.p}], s.p_forbidden],
        ]
        codes_prop_public = [
            [['getpublisheddetail', {'pk': self.p}], s.p_all],
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

        self.loop_phase_user(range(1,8), codes_general_phase1234567)
        self.loop_phase_user(range(1,8), codes_prop_notpublic)
        # self.loop_phase_user(range(1, 8), codes_anonymous_phase1234567)
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
