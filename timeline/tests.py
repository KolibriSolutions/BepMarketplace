from django.urls import reverse
from timeline.models import TimePhase
from datetime import datetime, timedelta
from general_test import ViewsTest


class TimeLineViewsTest(ViewsTest):
    def setUp(self):
        self.app = 'timeline'
        super().setUp()


    def test_view_status(self):
        ntp = TimePhase(Begin=datetime.now()+timedelta(days=1), End=datetime.now()+timedelta(days=3), Timeslot=self.ts, Description=1 )
        ntp.save()
        ptp = TimePhase(Begin=datetime.now()-timedelta(days=3), End=datetime.now()-timedelta(days=1), Timeslot=self.ts, Description=1 )
        ptp.save()

        codes = [
            [['list_timeslots',     None], self.p_support],
            [['add_timeslot',       None], self.p_support],

            [['edit_timeslot',      {'timeslot': self.ts.pk}], self.p_support],
            [['edit_timeslot',      {'timeslot': self.nts.pk}], self.p_support],
            [['edit_timeslot',      {'timeslot': self.pts.pk}], self.p_forbidden],

            [['list_timephases',    {'timeslot': self.ts.pk}], self.p_support],
            [['list_timephases',    {'timeslot': self.nts.pk}], self.p_support],
            [['list_timephases',    {'timeslot': self.pts.pk}], self.p_support],

            [['add_timephase',      {'timeslot': self.ts.pk}], self.p_support],
            [['add_timephase',      {'timeslot': self.nts.pk}], self.p_support],
            [['add_timephase',      {'timeslot': self.pts.pk}], self.p_forbidden],

            [['edit_timephase',     {'timephase': self.tp.pk}], self.p_support],
            [['edit_timephase',     {'timephase': ntp.pk}], self.p_support],
            [['edit_timephase',     {'timephase': ptp.pk}], self.p_forbidden],
        ]

        self.loop_phase_code_user(range(1, 8), codes)

        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
