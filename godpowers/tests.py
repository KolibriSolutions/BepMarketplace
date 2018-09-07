from general_test import ProjectViewsTestGeneral
from tracking.models import ProposalTracking


class GodpowersViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'godpowers'
        super().setUp()
        self.tracking = ProposalTracking(
            Subject=self.proposal,
        )
        self.tracking.save()

    def test_view_status(self):
        # godpowers are not tested, so this should return superuser for every normal user.
        codes_phase1234567 = [
            [['visitorsproposalsoverview', None], self.p_superuser],
            [['visitoroverview', {'pk': self.users['sup'].id}], self.p_superuser],
            [['visitorsmenu', None], self.p_superuser],
            [['clearcache', None], self.p_superuser],
            [['getvisitors', {'pk': self.tracking.id}], self.p_superuser],
            [['sessionlist', None], self.p_superuser],
            [['killsession', {'pk': self.users['sup'].id}], self.p_superuser],
        ]
        self.loop_phase_code_user(range(1, 8), codes_phase1234567)
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
