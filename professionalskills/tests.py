from datetime import datetime

from django.utils import timezone

from general_test import ProjectViewsTestGeneral
from timeline.utils import get_timeslot
from .models import FileType, StudentGroup


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

    def test_view_status(self):
        codes_general = [
            [['filetypecreate', None], self.p_support_prv],
            [['filetypeedit', {'pk': 100}], self.p_support_prv],
            [['filetypedelete', {'pk': 100}], self.p_support_prv],

            [['creategroup', {'pk': 100}], self.p_support_prv],
            [['creategroup', None], self.p_support_prv],
            [['editgroup', {'pk': 0}], self.p_support_prv],
            [['listgroups', {'pk': 100}], self.p_support_prv],
        ]
        codes_phase12345 = [  # also no-timephase
            [['listfileoftype', {'pk': 100}], self.p_forbidden],
            [['listmissingoftype', {'pk': 100}], self.p_forbidden],
            [['filetypelist', None], self.p_support_prv],
            [['liststudentfiles', {'pk': 1}], self.p_support_prv],
            [['listownfiles', None], self.p_forbidden],
            [['respondfile', {'pk': 0}], self.p_forbidden],
            [['mailoverduestudents', None], self.p_forbidden],
            [['printprvforms', None], self.p_forbidden],
            [['downloadall', {'pk': 0}], self.p_forbidden],
            [['listowngroups', None], self.p_forbidden],
            [['switchgroups', {'frompk': 0, 'topk': 1}], self.p_forbidden],
            [['listgroupmembers', {'pk': 0}], self.p_forbidden],
            [['assignshuffle', {'pk': 100}], self.p_forbidden],
        ]

        codes_phase67 = [
            [['listfileoftype', {'pk': 100}], self.p_support_prv],
            [['listmissingoftype', {'pk': 100}], self.p_support_prv],
            [['filetypelist', None], self.p_all],
            [['liststudentfiles', {'pk': 1}], self.p_all_this_dist],
            [['listownfiles', None], self.p_student],
            # [['respondfile', {'pk': 0}], self.p_all_this],# too complex to test
            [['mailoverduestudents', None], self.p_support_prv],
            [['printprvforms', None], self.p_support_prv],
            [['downloadall', {'pk': 100}], self.p_support_prv],

            [['listowngroups', None], self.p_student],
            # [['switchgroups', {'frompk': 0, 'topk': 1}], self.p_student], # never used and hard to test, so not tested
            [['listgroupmembers', {'pk': 0}], self.p_all],
            [['assignshuffle', {'pk': 100}], self.p_support_prv],
        ]
        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_general)
        self.info['type'] = 'phase'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5], codes_phase12345)
        # self.loop_phase_user([5], codes_phase5)
        self.loop_phase_code_user([6, 7], codes_phase67)

        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
