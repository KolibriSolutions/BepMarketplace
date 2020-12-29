#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User

from general_test import ViewsTest
from index.models import UserMeta
from support.models import PublicFile, CapacityGroup, MailTemplate


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
        # self.debug =True
        t = MailTemplate(
            Message='test',
            Subject='test',
            RecipientsStaff='[]',
            RecipientsStudents='[]',
        )
        t.pk = 1
        t.save()

    def test_view_status(self):
        codes_general_phase1234567 = [  # including no-timephase
            [['mailinglist', None], self.p_support],
            [['mailinglisttemplate', {'pk': 1}], self.p_support],
            [['mailingconfirm', None], self.p_forbidden],  # requires post
            [['mailingtemplates', None], self.p_support],
            [['deletemailingtemplate', {'pk': 1}], self.p_support],
            [['mailtrackheads', None], self.p_support],
            # [['stats', None], self.p_staff12345],
            # public files
            [['addfile', None], self.p_support],
            [['editfiles', None], self.p_support],

            # users
            [['verifyassistants', None], self.p_support],
            [['overruleusermeta', {'pk': self.dummy.id}], self.p_support],
            [['userinfo', {'pk': self.dummy.id}], self.p_support],
            [['usergroups', {'pk': self.users['r-3'].pk}], self.p_support],

            # capacity group
            [['listcapacitygroups', None], self.p_anonymous],
            [['groupadministratorsform', None], self.p_support],  # new groupadmin form
            [['addcapacitygroup', None], self.p_support],
            [['editcapacitygroup', {'pk': CapacityGroup.objects.get(ShortName='ES').id}], self.p_support],
            [['deletecapacitygroup', {'pk': CapacityGroup.objects.get(ShortName='ES').id}], self.p_support],
            # [['capacitygroupadministration', None], self.p_support],  # old groupadmin form.

            [['edit_tracks', None], self.p_support],

            # lists
            [['listusers', None], self.p_support_prv],
            [['toggledisable', {'pk': self.dummy.id}], [302 if x == 200 else x for x in self.p_support]],
            [['liststaff', None], self.p_support_prv],
            [['liststaffproposals', {'pk': 1}], self.p_support],
            [['editfile', {'pk': self.publicfile.id}], self.p_support],
            [['deletefile', {'pk': self.publicfile.id}], self.p_support],

            [['history', None], self.p_support],
            [['history_download', {'timeslot': self.pts.pk, 'download': 'students'}], self.p_support],
            [['history_download', {'timeslot': self.nts.pk, 'download': 'students'}], self.p_forbidden],
            [['history_download', {'timeslot': self.ts.pk, 'download': 'students'}], self.p_forbidden],
        ]

        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes_general_phase1234567)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
