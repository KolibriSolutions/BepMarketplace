from django.urls import reverse

from general_test import ViewsTest
from django.contrib.auth.models import User
from index.models import UserMeta
from support.models import PublicFile

class SupportViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'support'
        super().setUp()

    def test_view_status(self):
        codes_nophase_phase1234567 = [
            [['mailinglist', None], self.p_support],
            [['mailtrackheads', None],self.p_support],
            [['contentpolicy', None], self.p_support],
            [['stats', None], self.p_staff12345],
            # public files
            [['addfile', None], self.p_support],
            [['editfiles', None], self.p_support],

            # users
            [['verifyassistants', None], self.p_support],
            # lists
            [['privateproposals', None], self.p_support_prv],
            [['listusers', None], self.p_support_prv],
            [['clearcacheuserlist', None], self.p_support_prv],
            [['liststaff', None], self.p_support_prv],
            [['liststaffproposals', {'pk':1}], self.p_support],
            [['liststaffXls', None], self.p_support],
            [['listgroupproposals', None], self.p_cgadmin],
            [['listproposalsadvisor', None], self.p_study],
        ]

        codes_pubfile_phase1234567 = [
            [['editfile', {'pk' : 1}], self.p_support],
            [['deletefile', {'pk' : 1}], self.p_support],
        ]

        codes_dist_phase12 = [
            [['SupportListApplicationsDistributions', None], self.p_forbidden],
            [['SupportListDistributionsXls', None], self.p_forbidden],
        ]
        codes_dist_phase34567 = [
            [['SupportListApplicationsDistributions', None], self.p_support_prv],
            [['SupportListDistributionsXls', None], self.p_support_prv],
        ]
        codes_stud_phase123 = [
            [['liststudents', None], self.p_forbidden],
            [['liststudentsXls', None], self.p_forbidden]
        ]
        codes_stud_phase4567 = [
            [['liststudents', None], self.p_staff_stud],
            [['liststudentsXls', None], self.p_staff_stud]
        ]
        codes_users_phase1234567 = [
            [['upgradeuser', {'pk':100}], self.p_support],
            [['downgradeuser', {'pk':100}], self.p_support],
            [['overruleusermeta', {'pk':100}], self.p_support],
            [['userinfo', {'pk':100}], self.p_support]
        ]

        # not logged in users. Ignore status, only use the views column of permission matrix.
        # Status should be 302 always.
        self.info['type'] = 'not logged in'
        for page, status in codes_nophase_phase1234567:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
        for page, status in codes_dist_phase12:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
        for page, status in codes_stud_phase123:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)
        for page, status in codes_users_phase1234567:
            self.view_test_status(reverse(self.app+':'+page[0], kwargs=page[1]), 302)

        # Test for users
        self.info['type'] = 'logged in'
        self.loop_phase_user(range(1, 8), codes_nophase_phase1234567)

        self.loop_phase_user([1,2], codes_dist_phase12)
        self.loop_phase_user([3,4,5,6,7], codes_dist_phase34567)
        self.loop_phase_user([1,2,3], codes_stud_phase123)
        self.loop_phase_user([4,5,6,7], codes_stud_phase4567)

        # create dummy user for upgrade/downgrade
        u = User(username='dummy')
        u.id = 100
        u.save()
        m = UserMeta(User=u)
        m.save()
        self.loop_phase_user(range(1,8), codes_users_phase1234567)
        #create dummy public file for edit and delete
        pf = PublicFile(File='/home/django/dummy.txt')
        pf.save()
        self.loop_phase_user(range(1, 8), codes_pubfile_phase1234567)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")