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
            [['livestreamer', None], self.p_superuser],
            [['userdetail', {'pk': self.users['sup'].id}], self.p_superuser],
        ]

        # create dummy objects
        u = UserLogin(Subject=User.objects.get(username='r-s'))
        u.save()

        self.loop_phase_code_user(range(1, 8), codes)
        # check if all urls are processed
        self.assertListEqual(self.allurls, [], msg="Not all URLs of this app are tested!")
