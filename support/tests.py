from django.contrib.auth.models import User

from general_test import ViewsTest
from index.models import UserMeta
from support.models import PublicFile


class SupportViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'support'
        super().setUp()

        # create dummy user for upgrade/downgrade
        self.dummy = User(username='dummy')
        self.dummy.save()
        m = UserMeta(User=self.dummy)
        m.save()
        # create dummy public file for edit and delete
        self.publicfile = PublicFile(File='/home/django/dummy.txt')
        self.publicfile.save()

    def test_view_status(self):
        codes_general_phase1234567 = [  # including no-timephase
            [['mailinglist', None], self.p_support],
            [['mailtrackheads', None], self.p_support],
            [['contentpolicy', None], self.p_support],
            [['stats', None], self.p_staff12345],
            # public files
            [['addfile', None], self.p_support],
            [['editfiles', None], self.p_support],

            # users
            [['verifyassistants', None], self.p_support],
            [['capacitygroupadministration', None], self.p_support],
            [['overruleusermeta', {'pk': self.dummy.id}], self.p_support],
            [['userinfo', {'pk': self.dummy.id}], self.p_support],
            [['usergroups', {'pk': self.users['r-3'].pk}], self.p_support],

            # lists
            [['privateproposals', None], self.p_support_prv],
            [['listusers', None], self.p_support_prv],
            [['liststaff', None], self.p_support_prv],
            [['liststaffproposals', {'pk': 1}], self.p_support],
            [['liststaffXls', None], self.p_support],
            [['listgroupproposals', None], self.p_cgadmin],
            [['listproposalsadvisor', None], self.p_study],
            [['listnonfullprojects', None], self.p_support],
            [['listnonfullprojectsxlsx', {'timeslot': 1}], self.p_support],
            [['editfile', {'pk': self.publicfile.id}], self.p_support],
            [['deletefile', {'pk': self.publicfile.id}], self.p_support],
        ]
        codes_dist_phase12 = [
            [['SupportListApplicationsDistributions', None], self.p_forbidden],
            [['SupportListDistributionsXls', None], self.p_forbidden],
        ]
        codes_dist_phase34567 = [
            [['SupportListApplicationsDistributions', None], self.p_support_prv],
            [['SupportListDistributionsXls', None], self.p_support_prv],
        ]
        codes_stud_phase123 = [  # not available when applications/distributions have not yet been made.
            [['liststudents', None], self.p_forbidden],
            [['liststudentsXls', None], self.p_forbidden]
        ]
        codes_stud_phase4567 = [  # list students is also available when no-timephase (but not when no-timeslot)
            [['liststudents', None], self.p_staff_stud],
            [['liststudentsXls', None], self.p_staff_stud]
        ]

        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_general_phase1234567)
        self.loop_phase_code_user([-1, 1, 2], codes_dist_phase12)
        self.loop_phase_code_user([3, 4, 5, 6, 7], codes_dist_phase34567)
        self.loop_phase_code_user([1, 2, 3], codes_stud_phase123)
        self.loop_phase_code_user([-1, 4, 5, 6, 7], codes_stud_phase4567)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
