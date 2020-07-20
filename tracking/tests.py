#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User

from general_test import ViewsTest
from .models import UserLogin


class TrackingViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'tracking'
        super().setUp()

    def test_view_status(self):
        codes = [
            [['statuslist', None], self.p_superuser],  # god only
            [['applicationlist', None], self.p_superuser],  # god only
            [['listuserlog', None], self.p_superuser],
            [['userdetail', {'pk': self.users['sup'].id}], self.p_superuser],
        ]

        # create dummy objects
        u = UserLogin(Subject=User.objects.get(username='r-s'))
        u.save()

        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes)
        # check if all urls are processed
        # downloadtelemetry is different accesscontrolled so no test
        self.assertListEqual(self.allurls, ['downloadtelemetry'], msg="Not all URLs of this app are tested!")
