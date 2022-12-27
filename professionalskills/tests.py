#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import datetime

from django.utils import timezone

from general_test import ProjectViewsTestGeneral
from timeline.utils import get_timeslot
from .models import FileType, StudentGroup, StudentFile, StaffResponseFileAspect


class ProfessionalSkillsViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'professionalskills'
        super().setUp()

        # create a filetype for testing
        f = FileType(
            Name='testfiletype',
            TimeSlot=get_timeslot(),
            Deadline=datetime(year=2018, month=5, day=4)
        )
        f.id = 100
        f.save()
        fa = StaffResponseFileAspect(
            Name='Testaspect;',
            Description='TestAspectDescription',
            File=f,
        )
        fa.id = 100
        fa.save()
        sf = StudentFile(
            Caption='TestFile',
            Distribution=self.distribution_random,
            OriginalName='test.txt',
            Type=f,
        )
        sf.id = 0
        sf.save()
        g1 = StudentGroup(
            Number=0,
            PRV=f,
            Max=10,
            Start=timezone.now()
        )
        g1.id = 0
        # g1.Members.add(self.users['t-p'])
        # g1.Members.add(self.users['r-s'])
        g1.save()
        g2 = StudentGroup(
            Number=1,
            PRV=f,
            Max=10,
            Start=timezone.now()
        )
        g2.id = 1
        g2.save()
        g2.Members.add(self.users.get('r-s'))
        g2.Members.add(self.users.get('t-p'))
        g2.save()

    def test_view_status(self):
        codes_general = [
            [['create', None], self.p_support_prv],
            [['edit', {'pk': 100}], self.p_support_prv],
            [['delete', {'pk': 100}], self.p_support_prv],
            [['add_aspect', {'pk': 100}], self.p_support_prv],
            [['edit_aspect', {'pk': 100}], self.p_support_prv],
            [['delete_aspect', {'pk': 100}], self.p_support_prv],

            [['creategroup', {'pk': 100}], self.p_support_prv],
            [['creategroup', None], self.p_support_prv],
            [['extensions', None], self.p_support_prv],
            [['editgroup', {'pk': 0}], self.p_support_prv],
            [['listgroups', {'pk': 100}], self.p_support_prv],

            [['copy_filetypes_overview', None], self.p_support_prv],
            [['copy_filetypes', {'from_ts_pk': self.pts.pk}], self.p_forbidden],  # always forbidden because current ts already has prof skills.
            [['copy_aspects_overview', {'pk': 100}], self.p_support_prv],
            [['copy_aspects', {'pk': 100, 'from_pk': 100}], self.p_support_prv],  # copy from itself.
            [['filetype_export', {'pk': 100}], self.p_support_prv],  # copy from itself.

        ]
        codes_phase1234 = [  # also no-timephase
            [['listfileoftype', {'pk': 100}], self.p_forbidden],
            [['listmissingoftype', {'pk': 100}], self.p_forbidden],
            [['list', None], self.p_staff_veri],
            [['list_aspects', {'pk': 100}], self.p_support_prv],
            [['student', {'pk': 1}], self.p_forbidden],
            [['student', None], self.p_forbidden],
            [['respond', {'pk': 0}], self.p_forbidden],
            [['response', {'pk': 0}], self.p_forbidden],
            [['mailoverduestudents', None], self.p_forbidden],
            [['printprvforms', None], self.p_forbidden],
            [['downloadall', {'pk': 100}], self.p_forbidden],
            [['listowngroups', None], self.p_forbidden],
            [['switchgroups', {'pk': 100}], self.p_forbidden],
            [['listgroupmembers', {'pk': 0}], self.p_forbidden],
            [['assignshuffle', {'pk': 100}], self.p_forbidden],

            [['upload', {'pk': 100}], self.p_forbidden],

        ]

        codes_phase567 = [
            [['listfileoftype', {'pk': 100}], self.p_staff_stud],
            [['listmissingoftype', {'pk': 100}], self.p_staff_stud],
            [['list', None], self.p_staff_veri],
            [['list_aspects', {'pk': 100}], self.p_all],
            [['student', None], self.p_student],
            [['respond', {'pk': 0}], self.p_staff_prv_results],

            [['mailoverduestudents', None], self.p_support_prv],
            [['printprvforms', None], self.p_staff_stud],


            [['listowngroups', None], self.p_student],
            [['switchgroups', {'pk': 100}], self.p_student],  # never used and hard to test, so not tested
            [['listgroupmembers', {'pk': 0}], self.p_all],
            [['assignshuffle', {'pk': 100}], self.p_support_prv],

            [['upload', {'pk': 100}], self.p_student],
        ]
        codes_phase56_planning_hidden = [
            [['student', None], self.p_student],
            [['student', {'pk': self.distribution_random.pk}], self.p_all_this_dist],
            [['response', {'pk': 0}], self.p_all_this_dist_stud],
            [['downloadall', {'pk': 100}], self.p_all_this_dist],
        ]

        codes_phase7_planning_visible = [
            [['student', None], self.p_student],
            [['student', {'pk': self.distribution_random.pk}], self.p_all_this_dist_ta],
            [['response', {'pk': 0}], self.p_all_this_dist_ta_stud],
            [['downloadall', {'pk': 100}], self.p_all_this_dist_ta],
        ]
        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_general)
        self.info['type'] = 'phase'
        self.loop_phase_code_user([-1, 1, 2, 3, 4], codes_phase1234)
        self.loop_phase_code_user([5, 6, 7], codes_phase567)
        self.loop_phase_code_user([5, 6], codes_phase56_planning_hidden)

        self.loop_phase_code_user([7], codes_phase7_planning_visible)
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
