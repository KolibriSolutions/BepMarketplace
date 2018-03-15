from datetime import datetime

from django.urls import reverse

from general_test import ProposalViewsTest
from professionalskills.models import StudentFile, FileType
from .models import Distribution, Application


class StudentsViewsTest(ProposalViewsTest):
    def setUp(self):
        self.app = 'students'
        super().setUp()

    def test_view_status(self):
        """
        Test pages related to applications

        :return:
        """
        # Track for the proposal, with trackhead t-h
        s = self
        # General pages
        code_general_phase12 = [
            [['listapplications', None],          [s.p_forbidden]],
            [['addfile', None],                   [s.p_forbidden]],
            [['editfile', {'pk': 0}],                 [s.p_forbidden]],
        ]
        code_general_phase345 = [
            [['listapplications', None],          [s.p_student]],
            [['addfile', None],                   [s.p_forbidden]],
            [['editfile', {'pk': 0}],                 [s.p_forbidden]],
        ]
        code_general_phase67 = [
            [['listapplications', None],          [s.p_student]],
            [['addfile', None],                   [s.p_student]],
            [['editfile', {'pk': 0}],                 [s.p_student]],
        ]

        # Proposal specific pages
        code_phase124567 = [
            [['apply', {'pk': s.p}],               [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['confirmapply', {'pk': s.p}],        [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
        ]
        code_phase3 = [
            [['apply', {'pk': s.p}],               [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_studentnotpriv]],
            [['apply', {'pk': s.ppriv}],               [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['confirmapply', {'pk': s.p}],        [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_studentnotpriv]],
            [['confirmapply', {'pk': s.ppriv}],        [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
        ]
        code_application_none = [
            [['retractapplication', {'application_id': 0}], [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['prioUp', {'application_id': 0}],             [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]],
            [['prioDown', {'application_id': 0}],           [s.p_forbidden, s.p_forbidden, s.p_forbidden, s.p_forbidden]]
        ]



        s.status = 1
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if s.debug:
            print("not logged in users")
        self.info['type'] = 'not logged in'
        for page, status in code_general_phase12:
            s.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
        for page, status in code_phase3:
            s.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
        for page, status in code_application_none:
            s.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
            if page[0] in self.allurls: self.allurls.remove(page[0])

        # Test general page (not proposal specific)
        if s.debug:
            print("Testing general without stats")

        # In phase 6 and 7 a distribution is needed
        d = Distribution(Student=s.users.get('r-s'), Proposal=s.proposal, Timeslot=s.ts)
        d.save()
        d = Distribution(Student=s.users.get('t-p'), Proposal=s.privateproposal, Timeslot=s.ts)
        d.save()
        t = FileType(
            Description='type 0',
            Deadline=datetime.now(),
            TimeSlot=self.ts,
        )
        t.save()
        f = StudentFile(
            Distribution=d,
            Caption='File 0',
            Type=t,
        )
        f.pk = 0
        f.save()

        self.info['type'] = 'general'
        self.loop_phase_user([1,2], code_general_phase12)
        self.loop_phase_user([3,4,5], code_general_phase345)
        self.loop_phase_user([6,7], code_general_phase67)

        if s.debug:
            print("Testing proposal apply")
        self.info['type'] = 'apply this timeslot'
        self.loop_phase_user([1, 2, 4, 5, 6, 7], code_phase124567)
        self.loop_phase_user([3], code_phase3)

        # Proposal specific for proposal of other timeslot, never allow apply
        self.info['type'] = 'apply prev timeslot'
        s.proposal.TimeSlot = s.pts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.pts
        s.privateproposal.save()
        # this code matrix has forbidden everywhere (because apply is not possible for other timeslot)
        self.loop_phase_user(range(1, 8), code_phase124567)

        self.info['type'] = 'apply next timeslot'
        s.proposal.TimeSlot = s.nts
        s.proposal.save()
        s.privateproposal.TimeSlot = s.nts
        s.privateproposal.save()
        self.loop_phase_user(range(1, 8), code_phase124567)

        # make sure all urls are tested.
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")

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