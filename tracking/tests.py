from django.urls import reverse

from general_test import ViewsTest


class TrackingViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'tracking'
        super().setUp()

    def test_view_status(self):
        codes = [
            [['statuslist', None], self.p_forbidden],  # god only
            [['applicationlist', None], self.p_forbidden],  # god only
            [['listuserlog', None], self.p_forbidden],
            [['livestreamer', None], self.p_forbidden],
            [['userdetail', {'pk': 0}], self.p_forbidden],
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)

        # Test for users
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 8), codes)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")