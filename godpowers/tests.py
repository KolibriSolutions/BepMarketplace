from django.urls import reverse

from general_test import ViewsTest


class GodpowersViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'godpowers'
        super().setUp()

    def test_view_status(self):
        # godpowers are not tested, so this should return forbidden for every normal user.
        codes_phase1234567 = [
            [['visitorsproposalsoverview', None], self.p_forbidden],
            [['visitoroverview', {'pk':0}], self.p_forbidden],
            [['visitorsmenu', None], self.p_forbidden],
            [['clearcache', None], self.p_forbidden],
            [['groupadministration', None], self.p_forbidden],
            [['getvisitors', {'pk': 0}], self.p_forbidden],
            [['sessionlist', None], self.p_forbidden],
            [['killsession', {'pk':0}], self.p_forbidden],
        ]
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes_phase1234567:
            self.view_test_status(reverse(self.app + ':' + page[0], kwargs=page[1]), 302)

        # Test for users, testing with nonexistent files for simplicity. So this always returns 404
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 8), codes_phase1234567)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")