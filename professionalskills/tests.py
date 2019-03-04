from datetime import datetime

from django.utils import timezone

from general_test import ProjectViewsTestGeneral
from timeline.utils import get_timeslot
from .models import FileType, StudentGroup, StudentFile


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
        sf = StudentFile(
            Caption='TestFile',
            Distribution=self.distribution_random,
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
            [['filetypecreate', None], self.p_support_prv],
            [['filetypeedit', {'pk': 100}], self.p_support_prv],
            [['filetypedelete', {'pk': 100}], self.p_support_prv],

            [['creategroup', {'pk': 100}], self.p_support_prv],
            [['creategroup', None], self.p_support_prv],
            [['extensions', None], self.p_support_prv],
            [['editgroup', {'pk': 0}], self.p_support_prv],
            [['listgroups', {'pk': 100}], self.p_support_prv],
        ]
        codes_phase1234 = [  # also no-timephase
            [['listfileoftype', {'pk': 100}], self.p_forbidden],
            [['listmissingoftype', {'pk': 100}], self.p_forbidden],
            [['filetypelist', None], self.p_support_prv],
            [['liststudentfiles', {'pk': 1}], self.p_support_prv],
            [['listownfiles', None], self.p_forbidden],
            [['respondfile', {'pk': 0}], self.p_forbidden],
            [['viewresponse', {'pk': 0}], self.p_forbidden],
            [['mailoverduestudents', None], self.p_forbidden],
            [['printprvforms', None], self.p_forbidden],
            [['downloadall', {'pk': 100}], self.p_forbidden],
            [['listowngroups', None], self.p_forbidden],
            [['switchgroups', {'pk': 100}], self.p_forbidden],
            [['listgroupmembers', {'pk': 0}], self.p_forbidden],
            [['assignshuffle', {'pk': 100}], self.p_forbidden],
        ]

        codes_phase567 = [
            [['listfileoftype', {'pk': 100}], self.p_support_prv],
            [['listmissingoftype', {'pk': 100}], self.p_support_prv],
            [['filetypelist', None], self.p_all],
            [['liststudentfiles', {'pk': 1}], self.p_all_this_dist],
            [['listownfiles', None], self.p_student],
            [['respondfile', {'pk': 0}], self.p_staff_prv_results],
            [['viewresponse', {'pk': 0}], self.p_all_this_dist],

            [['mailoverduestudents', None], self.p_support_prv],
            [['printprvforms', None], self.p_support_prv],
            [['downloadall', {'pk': 100}], self.p_support_prv],

            [['listowngroups', None], self.p_student],
            [['switchgroups', {'pk': 100}], self.p_student], # never used and hard to test, so not tested
            [['listgroupmembers', {'pk': 0}], self.p_all],
            [['assignshuffle', {'pk': 100}], self.p_support_prv],
        ]
        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_general)
        self.info['type'] = 'phase'
        self.loop_phase_code_user([-1, 1, 2, 3, 4], codes_phase1234)
        # self.loop_phase_user([5], codes_phase5)
        self.loop_phase_code_user([5, 6, 7], codes_phase567)
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
