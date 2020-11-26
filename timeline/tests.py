#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import datetime, timedelta

from general_test import ViewsTest
from timeline.models import TimePhase


class TimeLineViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'timeline'
        super().setUp()

    def test_view_status(self):
        # number of days should be larger than settings.
        # TIMELINE_EDIT_DAYS_AFTER_FINISH = 30  # number of days after which a timeslot/timephase has ended, after which editing of the timeslot/phase is disabled.

        ntp = TimePhase(Begin=datetime.now() + timedelta(days=100), End=datetime.now() + timedelta(days=300),
                        TimeSlot=self.ts, Description=1)
        ntp.save()
        ptp = TimePhase(Begin=datetime.now() - timedelta(days=300), End=datetime.now() - timedelta(days=100),
                        TimeSlot=self.ts, Description=1)
        ptp.save()

        codes = [
            [['list_timeslots', None], self.p_support],
            [['add_timeslot', None], self.p_support],
            [['copy_timephases', None], self.p_support],
            [['delete_timephase', {'timephase': self.tp.pk}], self.p_support],

            [['edit_timeslot', {'timeslot': self.ts.pk}], self.p_support],
            [['edit_timeslot', {'timeslot': self.nts.pk}], self.p_support],
            [['edit_timeslot', {'timeslot': self.pts.pk}], self.p_forbidden],

            [['list_timephases', {'timeslot': self.ts.pk}], self.p_support],
            [['list_timephases', {'timeslot': self.nts.pk}], self.p_support],
            [['list_timephases', {'timeslot': self.pts.pk}], self.p_support],

            [['add_timephase', {'timeslot': self.ts.pk}], self.p_support],
            [['add_timephase', {'timeslot': self.nts.pk}], self.p_support],
            [['add_timephase', {'timeslot': self.pts.pk}], self.p_forbidden],

            [['edit_timephase', {'timephase': self.tp.pk}], self.p_support],
            [['edit_timephase', {'timephase': ntp.pk}], self.p_support],
            [['edit_timephase', {'timephase': ptp.pk}], self.p_forbidden],
        ]

        self.loop_phase_code_user([-1, 1, 2, 3, 4, 5, 6, 7], codes)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
