from django.urls import reverse

from general_test import ProposalViewsTest
from students.models import Distribution, Application


class StudentsViewsTest(ProposalViewsTest):

    def test_view_status(self):
        """
        Test pages related to applications

        :return:
        """
        # Track for the proposal, with trackhead t-h
        self.setup()
        self.debug = False
        app = 'students:'
        # expected results:
        # r=random, t=this(for this proposal)
        # s=student, p=private-student, r=responsible, a=assistant, n = assistant_not_verified t=trackhead, u=support
        # matrix with different types of permissions, set for each user of the array self.usernames

        #  usernames = ['r-3', 'r-s' 't-p', 'r-1', 't-1', 'r-2',   't-2',  't-u',  'r-h',  't-h']
        forbidden =    [403,   403,   403,   403,    403,    403,    403,    403,     403,    403]  # no one
        student =      [403,   200,   200,   403,    403,    403,    403,    403,     403,    403]  # no one
        studentnotpriv=[403,   200,   403,   403,    403,    403,    403,    403,     403,    403]  # no one

        # General pages
        code_general_phase12 = [
            [['listapplications'],          [forbidden]],
            [['addfile'],                   [forbidden]],
            [['editfiles'],                 [forbidden]],
        ]
        code_general_phase345 = [
            [['listapplications'],          [student]],
            [['addfile'],                   [forbidden]],
            [['editfiles'],                 [forbidden]],
        ]
        code_general_phase67 = [
            [['listapplications'],          [student]],
            [['addfile'],                   [student]],
            [['editfiles'],                 [student]],
        ]

        # Proposal specific pages
        code_phase124567 = [
            [['apply', {'pk': self.p}],               [forbidden, forbidden, forbidden, forbidden]],
            [['confirmapply', {'pk': self.p}],        [forbidden, forbidden, forbidden, forbidden]],
        ]
        code_phase3 = [
            [['apply', {'pk': self.p}],               [forbidden, forbidden, forbidden, studentnotpriv]],
            [['apply', {'pk': self.ppriv}],               [forbidden, forbidden, forbidden, forbidden]],
            [['confirmapply', {'pk': self.p}],        [forbidden, forbidden, forbidden, studentnotpriv]],
            [['confirmapply', {'pk': self.ppriv}],        [forbidden, forbidden, forbidden, forbidden]],
        ]
        code_application_none = [
            [['retractapplication', {'application_id': 0}], [forbidden, forbidden, forbidden, forbidden]],
            [['prioUp', {'application_id': 0}],             [forbidden, forbidden, forbidden, forbidden]],
            [['prioDown', {'application_id': 0}],           [forbidden, forbidden, forbidden, forbidden]]
        ]

        self.status = 1
        # info object with debug info if assertion fails
        info = {}
        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        if self.debug:
            print("not logged in users")
        info['type'] = 'not logged in'
        for page, status in code_general_phase12:
            self.view_test_status(app+page[0], 302)
        for page, status in code_phase3:
            self.view_test_status(app+page[0], 302, kw=page[1])
        for page, status in code_application_none:
            self.view_test_status(app+page[0], 302, kw=page[1])

        # Test general page (not proposal specific)
        if self.debug:
            print("Testing general without stats")
        info['type'] = 'general'
        for phase in [1, 2]:
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('General 1, phase {}'.format(phase))
            info['phase'] = str(phase)
            for page, status in code_general_phase12:
                self.loop_user_status(app+page[0], status, info)

        for phase in [3, 4, 5]:
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('General 2, phase {}'.format(phase))
            info['phase'] = str(phase)
            for page, status in code_general_phase345:
                self.loop_user_status(app+page[0], status, info)

        # In phase 6 and 7 a distribution is needed
        d = Distribution(Student=self.users.get('r-s'), Proposal=self.proposal, Timeslot=self.ts)
        d.save()
        d = Distribution(Student=self.users.get('t-p'), Proposal=self.privateproposal, Timeslot=self.ts)
        d.save()

        for phase in [6, 7]:
            self.tp.Description = phase
            self.tp.save()
            info['phase'] = str(phase)
            if self.debug:
                print('General 3, phase {}'.format(phase))
            for page, status in code_general_phase67:
                self.loop_user_status(app+page[0], status, info)

        # Test proposal specific page
        if self.debug:
            print("Testing proposal apply")
        info['type'] = 'apply'
        for phase in [1, 2, 4, 5, 6, 7]:
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('Apply (closed), phase {}'.format(phase))
            info['phase'] = str(phase)
            for page, status in code_phase124567:
                self.loop_user_status(app+page[0], status, info, kw=page[1])

        phase = 3
        self.tp.Description = phase
        self.tp.save()
        if self.debug:
            print('Apply (open), phase {}'.format(phase))
        info['phase'] = str(phase)
        for page, status in code_phase3:
            self.loop_user_status(app+page[0], status, info, kw=page[1])

        # Proposal specific for proposal of other timeslot, never allow apply

        if self.debug:
            print("Testing proposal apply")
        info['type'] = 'apply'
        self.proposal.TimeSlot = self.pts
        self.proposal.save()
        self.privateproposal.TimeSlot = self.pts
        self.privateproposal.save()
        for phase in range(1, 8):
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('Apply other timeslot, phase {}'.format(phase))
            info['phase'] = str(phase)
            # this code matrix has forbidden everywhere (because apply is not possible for other timeslot)
            for page, status in code_phase124567:
                self.loop_user_status(app+page[0], status, info, kw=page[1])

        if self.debug:
            print("Testing proposal apply")
        info['type'] = 'apply'
        self.proposal.TimeSlot = self.nts
        self.proposal.save()
        self.privateproposal.TimeSlot = self.nts
        self.privateproposal.save()
        for phase in range(1, 8):
            self.tp.Description = phase
            self.tp.save()
            if self.debug:
                print('Apply other timeslot, phase {}'.format(phase))
            info['phase'] = str(phase)
            # this code matrix has forbidden everywhere (because apply is not possible for other timeslot)
            for page, status in code_phase124567:
                self.loop_user_status(app+page[0], status, info, kw=page[1])

    def test_apply_retract(self):
        """
        Test apply retract pages in phase 3

        :return:
        """
        self.setup()
        self.tp.Description = 3
        self.tp.save()
        self.proposal.Status = 4
        self.proposal.save()

        # student
        s = self.users.get('r-s')

        # Test apply
        view = "students:apply"
        self.client.login_user(s)
        response = self.client.get(reverse(view, kwargs={"pk": self.p}))
        self.assertEqual(response.status_code, 200, msg="Student cannot apply to proposal!")

        self.assertTrue(Application.objects.exists(), msg="Application is not made!")

        # Test retract
        view = "students:retractapplication"
        app = Application.objects.get(Student=s)
        response = self.client.get(reverse(view, kwargs={"application_id": app.id}))
        self.assertEqual(response.status_code, 200, msg="Student cannot retract application!")

        self.assertFalse(Application.objects.exists(), msg="Application is not retracted!")

        self.client.logout_user(s)