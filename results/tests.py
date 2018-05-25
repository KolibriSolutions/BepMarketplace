from django.urls import reverse

from general_test import ProjectViewsTestGeneral
from students.models import Distribution
from .models import GradeCategoryAspect, GradeCategory, ResultOptions


class TrackingViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'results'
        super().setUp()

    def test_view_status(self):
        c = GradeCategory(
            Name='cat-a',
            Weight=100,
            TimeSlot=self.ts,
        )
        c.save()
        a = GradeCategoryAspect(
            Category=c,
            Name='asp-a',
            Description='test',
        )
        a.save()

        # make a distribution, this gets id 1.
        d = Distribution(
            Proposal=self.proposal,
            Student=self.users['r-s'],
            Timeslot=self.ts,
        )
        d.save()
        v = ResultOptions(
            TimeSlot=self.ts
        )
        v.save()

        codes_nophase = [
            [['about', None], self.p_all],

            [['list_categories', None], self.p_support],
            [['add_category', None], self.p_support],
            [['edit_category', {'pk': c.pk}], self.p_support],
            [['list_aspects', {'pk': c.pk}], self.p_support],
            [['add_aspect', {'pk': c.pk}], self.p_support],
            [['edit_aspect', {'pk': a.pk}], self.p_support],
            [['delete_aspect', {'pk': a.pk}], self.p_support],
            [['delete_category', {'pk': c.pk}], self.p_support],
            [['copy_overview', None], self.p_support],
            [['copy', {'pk': self.pts.pk}], self.p_support],
        ]

        codes_phase12345 = [
            [['gradeformstaff', {'pk': d.pk}], self.p_forbidden],
            [['gradeformstaff', {'pk': d.pk, 'step': 0}], self.p_forbidden],
            [['gradefinal', {'pk': d.pk}], self.p_forbidden],
            [['gradefinal', {'pk': d.pk, 'version': 0}], self.p_forbidden],
        ]
        codes_phase67_notvisible = [
            [['gradeformstaff', {'pk': d.pk}], self.p_forbidden],
            [['gradeformstaff', {'pk': d.pk, 'step': 0}], self.p_forbidden],
            [['gradefinal', {'pk': d.pk}], self.p_forbidden],
            [['gradefinal', {'pk': d.pk, 'version': 0}], self.p_forbidden],
        ]
        codes_phase67_visible = [
            [['gradeformstaff', {'pk': d.pk}], self.p_no_assistant],
            [['gradeformstaff', {'pk': d.pk, 'step': 0}], self.p_no_assistant],
            [['gradefinal', {'pk': d.pk}], self.p_trackhead_only],
            [['gradefinal', {'pk': d.pk, 'version': 0}], self.p_trackhead_only],
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes_phase12345:
            self.view_test_status(reverse(self.app + ':' + page[0], kwargs=page[1]), 302)

        # Test for users
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 6), codes_phase12345)
        self.loop_phase_user(range(1, 8), codes_nophase)

        self.loop_phase_user([6, 7], codes_phase67_notvisible)
        v.Visible = True
        v.save()
        self.loop_phase_user([6, 7], codes_phase67_visible)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
