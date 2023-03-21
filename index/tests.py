#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.urls import reverse
from django.utils import timezone

from general_test import ProjectViewsTestGeneral, ViewsTest
from .models import FeedbackReport


class IndexViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'index'
        super().setUp()
        # self.debug = True

        self.fb = FeedbackReport(
            Reporter=self.users['sup'],
            Url='/',
            Feedback='Test Feedback',
            Timestamp=timezone.now(),
            Status=1,
        )
        self.fb.save()
        self.privateproposal.Status = 4  # to let private student view its proposal
        self.privateproposal.save()
        self.proposal.Status = 4  # to let private student view its proposal
        self.proposal.save()

    def test_view_status(self):
        self.info = {}
        codes_status = [
            [['index', None], self.p_anonymous],
            [['about', None], self.p_anonymous],
            [['profile', None], self.p_all],
            [['feedback_form', None], self.p_all],
            [['feedback_submit', None], self.p_all],
            [['list_feedback', None], self.p_superuser],  # god only
            [['confirm_feedback', {'pk': self.fb.id}], self.p_superuser],  # god only
            [['close_feedback', {'pk': self.fb.id}], self.p_superuser],  # god only
            [['changesettings', None], self.p_all],
            [['termsaccept', None], self.p_redirect],
            [['robots', None], self.p_anonymous],
        ]

        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_status)
        # check if all urls are processed, except login and logout
        self.assertListEqual(self.allurls, ['2falogin', 'login', 'logout'], msg="Not all URLs of this app are tested!")

    def test_links_visible(self):
        """
        Test if all links shown in a view go to a page with status 200.
        Used to test if all visible menu items are actually available for the given user in the given view.

        :return:
        """
        self.info = {}
        views = ["index:index", 'index:profile']
        for phase in range(1, 8):
            self.info['phase'] = str(phase)
            self.tp.Description = phase
            self.tp.save()
            for view in views:
                self.info['view'] = view
                ViewsTest.links_in_view_test(self, reverse(view))
