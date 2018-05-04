from django.urls import reverse

from general_test import ProposalViewsTest


class DownloadViewsTest(ProposalViewsTest):
    def setUp(self):
        self.app = 'download'
        super().setUp()

    def test_view_status(self):
        codes_phase1234567 = [
            [['publicfile', {'fileid': 0}], self.p_404],
            [['public_files', {'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf', 'timeslot': 0}], self.p_404],

            # proposal attachements
            [['proposalfile', {'ty':'a', 'fileid':0}], self.p_404],
            [['proposal_files', {'proposalid': 0, 'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf'}], self.p_404],

            # student files (professionalskills)
            [['studentfile', {'fileid': 0}], self.p_404],
            [['student_files', {'distid': 0, 'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf'}], self.p_404],
        ]
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 403, not 302 as this could be accessed via shared proposal
        # self.info['type'] = 'not logged in'
        # for page, status in codes_phase1234567:
        #     self.view_test_status(reverse(self.app + ':' + page[0], kwargs=page[1]), 403)

        # Test for users, testing with nonexistent files for simplicity. So this always returns 404
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 8), codes_phase1234567)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")