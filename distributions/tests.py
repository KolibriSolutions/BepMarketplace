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
            [['distributeproposal', {'dist_type': 1}], self.p_forbidden],
            [['distributeproposal', {'dist_type': 2}], self.p_forbidden],
            [['distributeproposaloption', {'dist_type': 2, 'distribute_random': 0, 'automotive_preference': 0}], self.p_forbidden],
            [['maildistributions', None], self.p_forbidden],
            [['automaticoptions', None], self.p_forbidden],
        ]
        codes_phase45 = [
            [['distribute', None], self.p_forbidden],
            [['undistribute', None], self.p_forbidden],
            [['changedistribute', None], self.p_forbidden],
            [['distributeproposal', {'dist_type': 1}], self.p_support],
            [['distributeproposal', {'dist_type': 2}], self.p_support],
            [['distributeproposaloption', {'dist_type': 2, 'distribute_random': 0, 'automotive_preference': 0}],
             self.p_support],
            [['maildistributions', None], self.p_support],
            [['automaticoptions', None], self.p_support],
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
        self.loop_phase_code_user([-1, 1, 2, 3, 6, 7], codes_phase12367)
        self.loop_phase_code_user([-1, 1, 2, 3, 7], codes_phase1237)
        self.loop_phase_code_user([4, 5, 6], codes_phase456)
        self.loop_phase_code_user([4, 5], codes_phase45)
        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
