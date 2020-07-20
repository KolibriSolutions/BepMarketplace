#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import reverse

from general_test import ProjectViewsTestGeneral


class DownloadViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'download'
        super(DownloadViewsTest, self).setUp()

    def test_view_status(self):
        codes_phase1234567 = [
            [['publicfile', {'fileid': 0}], self.p_404],
            [['public_files', {'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf', 'timeslot': 0}], self.p_404],

            # proposal attachements
            [['proposalfile', {'ty': 'a', 'fileid': 0}], self.p_download_share],
            [['proposal_files', {'project_id': 0, 'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf'}], self.p_download_share],
            # proposal attachements
            [['projectfile', {'ty': 'a', 'fileid': 0}], self.p_download_share],
            [['project_files', {'project_id': 0, 'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf'}], self.p_download_share],

            # student files (professionalskills)
            [['studentfile', {'fileid': 0}], self.p_404],
            [['student_files', {'distid': 0, 'fileid': '9b73c48b-e05f-4e08-9db5-c8100119f673.pdf'}], self.p_404],
        ]
        # Test for users, testing with nonexistent files for simplicity. So this always returns 404
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_phase1234567)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
