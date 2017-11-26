from django.urls import reverse

from general_test import ProposalViewsTest
from students.models import Distribution

class TrackingViewsTest(ProposalViewsTest):
    def setUp(self):
        self.app = 'results'
        super().setUp()

    def test_view_status(self):
        codes_phase123456 = [
            [['about', None], self.p_allowed],
            [['gradeformstaff', {'pk':1}], self.p_forbidden],
            [['gradeformstaff', {'pk':1, 'step':0}], self.p_forbidden],
            [['gradefinal', {'pk':1}], self.p_forbidden],
            [['gradefinal', {'pk':1, 'version':0}], self.p_forbidden],
        ]
        codes_phase7 = [
            [['about', None], self.p_allowed],
            [['gradeformstaff', {'pk':1}], self.p_trackhead_only],
            [['gradeformstaff', {'pk':1, 'step':0}], self.p_trackhead_only],
            [['gradefinal', {'pk':1}], self.p_trackhead_only],
            [['gradefinal', {'pk':1, 'version':0}], self.p_trackhead_only],
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes_phase123456:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)

        # make a distribution, this gets id 1.
        d = Distribution(
            Proposal=self.proposal,
            Student=self.users['r-s'],
            Timeslot=self.ts,
        )
        d.save()


        # Test for users
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 7), codes_phase123456)
        self.loop_phase_user([7], codes_phase7)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")