from general_test import ViewsTest


class OsirisDataTest(ViewsTest):
    def setUp(self):
        self.app = 'osirisdata'
        super().setUp()

    def test_view_status(self):
        codes = [
            [['list', None], self.p_support],
            [['tometa', None], self.p_support],
        ]
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
