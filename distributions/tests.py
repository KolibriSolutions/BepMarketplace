from django.urls import reverse

from general_test import ViewsTest


class DistributionsViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'distributions'
        super().setUp()

    def test_view_status(self):
        codes_phase12367 = [
            [['distribute', None], self.p_forbidden],
            [['undistribute', None], self.p_forbidden],
            [['changedistribute', None], self.p_forbidden],
            [['distributeproposal', {'dtype': 1}], self.p_forbidden],
            [['distributeproposal', {'dtype': 2}], self.p_forbidden],
            [['maildistributions', None], self.p_forbidden],
        ]
        codes_phase45 = [
            [['distribute', None], self.p_forbidden],
            [['undistribute', None], self.p_forbidden],
            [['changedistribute', None], self.p_forbidden],
            [['distributeproposal', {'dtype': 1}], self.p_support],
            [['distributeproposal', {'dtype': 2}], self.p_support],
            [['maildistributions', None], self.p_support],
        ]
        codes_phase1237 = [
            [['supportDistributeApplications', None], self.p_forbidden],
            [['secondchoice', None], self.p_forbidden],
            [['deleterandoms', None], self.p_forbidden],
        ]
        codes_phase456 = [
            [['supportDistributeApplications', None], self.p_support],
            [['secondchoice', None], self.p_support],
            [['deleterandoms', None], self.p_support],
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if self.debug:
            print("not logged in users")
        for page, status in codes_phase12367:
            self.view_test_status(reverse(self.app + ":" + page[0], kwargs=page[1]), 302)

        if self.debug:
            print("Logged in users")
        self.loop_phase_user([1,2,3,6,7], codes_phase12367)
        self.loop_phase_user([1,2,3,7], codes_phase1237)
        self.loop_phase_user([4,5,6], codes_phase456)
        self.loop_phase_user([4,5], codes_phase45)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
