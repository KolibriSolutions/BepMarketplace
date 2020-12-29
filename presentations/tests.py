#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from general_test import ViewsTest


class PresentationsViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'presentations'
        super().setUp()

    def test_view_status(self):
        codes_phase1234 = [  # also in no-timephase everything should be forbidden.
            [['presentationswizardstep1', None], self.p_forbidden],
            [['presentationswizardstep2', None], self.p_forbidden],
            [['presentationswizardstep2_edit', {"kind":"add"}], self.p_forbidden],
            [['presentationswizardstep2_edit', {"kind":"edit"}], self.p_forbidden],
            [['presentationswizardstep2_edit', {"kind": "asdf"}], self.p_forbidden],

            [['presentationswizardstep3', None], self.p_forbidden],
            [['presentationswizardstep4', None], self.p_forbidden],
            [['presentationsplanning', None], self.p_forbidden],
            [['presentationsplanningxls', None], self.p_forbidden],
            [['presentationscalendar', None], self.p_forbidden],
        ]
        codes_phase567 = [
            [['presentationswizardstep1', None], self.p_support],
            [['presentationswizardstep2', None], self.p_support],
            [['presentationswizardstep2_edit', {"kind": "add"}], self.p_support],
            [['presentationswizardstep2_edit', {"kind": "edit"}], self.p_support],
            [['presentationswizardstep3', None], self.p_support],
            [['presentationswizardstep4', None], self.p_support],
            [['presentationsplanning', None], self.p_support],
            [['presentationsplanningxls', None], self.p_all],
            # only truely visible when presentations are set to public or phase =7
            [['presentationscalendar', None], self.p_all],
            [['presentationscalendarown', None], self.p_all],
        ]

        self.loop_phase_code_user([-1, 1, 2, 3, 4], codes_phase1234)
        self.loop_phase_code_user([5, 6, 7], codes_phase567)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
