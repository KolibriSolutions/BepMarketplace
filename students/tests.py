from datetime import datetime

from django.urls import reverse

from general_test import ProjectViewsTestGeneral
from professionalskills.models import StudentFile, FileType
from .models import Application


class StudentsViewsTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'students'
        super().setUp()
        # self.debug = True

    def test_view_status(self):
        """
        Test pages related to applications

        :return:
        """
        # Track for the proposal, with trackhead t-h
        s = self
        a = Application(
            Priority=1,
            Proposal=s.proposal,
            Student=self.users['r-s'],
        )
        a.save()

        t = FileType(
            Description='type 0',
            Deadline=datetime.now(),
            TimeSlot=self.ts,
        )
        t.save()
        f = StudentFile(
            Distribution=self.distribution_random,
            Caption='File 0',
            Type=t,
        )
        f.save()

        s.status = 1

        # General pages
        code_general_phase12 = [
            [['listapplications', None], s.p_forbidden],
            [['addfile', None], s.p_forbidden],
            [['editfile', {'pk': f.pk}], s.p_forbidden],
        ]
        code_general_phase345 = [
            [['listapplications', None], s.p_student],
            [['addfile', None], s.p_forbidden],
            [['editfile', {'pk': f.pk}], s.p_forbidden],
        ]
        code_general_phase67 = [
            [['listapplications', None], s.p_student],
            [['addfile', None], s.p_student],
            [['editfile', {'pk': f.pk}], s.p_student],
        ]

        # Proposal specific pages
        code_phase124567 = [
            [['apply', {'pk': s.p}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['confirmapply', {'pk': s.p}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['apply', {'pk': s.ppriv}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['confirmapply', {'pk': s.ppriv}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
        ]
        code_phase3 = [
            [['apply', {'pk': s.p}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_studentnotpriv]],
            [['apply', {'pk': s.ppriv}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['confirmapply', {'pk': s.p}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_studentnotpriv]],
            [['confirmapply', {'pk': s.ppriv}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
        ]

        self.info['type'] = 'general'
        self.loop_phase_code_user([-1, 1, 2], code_general_phase12)
        self.loop_phase_code_user([3, 4, 5], code_general_phase345)
        self.loop_phase_code_user([6, 7], code_general_phase67)

        if s.debug:
            print("Testing proposal apply")
        self.info['type'] = 'apply this timeslot'
        self.loop_phase_code_user([-1, 1, 2, 4, 5, 6, 7], code_phase124567)
        self.loop_phase_code_user([3], code_phase3)

        # Proposal specific for proposal of other timeslot, never allow apply
        self.info['type'] = 'apply prev timeslot'
        s.proposal.TimeSlot = s.pts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.pts
        s.privateproposal.save()
        # this code matrix has forbidden everywhere (because apply is not possible for other timeslot)
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_phase124567)

        self.info['type'] = 'apply next timeslot'
        s.proposal.TimeSlot = s.nts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.nts
        s.privateproposal.save()
        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], code_phase124567)

        # make sure all urls are tested.
        # prio up / down and retract are not tested.
        self.assertListEqual(self.allurls, ['prioUp', 'prioDown', 'retractapplication'], msg="Not all URLs of this app are tested!")

    def test_apply_retract(self):
        """
        Test apply retract pages in phase 3

        :return:
        """
        self.tp.Description = 3
        self.tp.save()
        self.proposal.Status = 4
        self.proposal.save()

        # student
        stud = self.users.get('r-s')

        # Test apply
        view = "students:apply"
        self.client.force_login(stud)
        response = self.client.get(reverse(view, kwargs={"pk": self.p}))
        self.assertEqual(response.status_code, 200, msg="Student cannot apply to proposal!")

        self.assertTrue(Application.objects.exists(), msg="Application is not made!")

        # Test retract
        view = "students:retractapplication"
        app = Application.objects.get(Student=stud)
        response = self.client.get(reverse(view, kwargs={"application_id": app.id}))
        self.assertEqual(response.status_code, 200, msg="Student cannot retract application!")

        self.assertFalse(Application.objects.exists(), msg="Application is not retracted!")

        self.client.logout()
