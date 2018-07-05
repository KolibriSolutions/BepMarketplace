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
        self.loop_phase_user(range(1, 8), codes)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
