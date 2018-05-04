from general_test import ViewsTest
from django.urls import reverse

class OsirisDataTest(ViewsTest):
    def setUp(self):
        self.app = 'osirisdata'
        super().setUp()

    def test_view_status(self):
        codes = [
            [['list', None], self.p_support],
            [['tometa', None], self.p_support],
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