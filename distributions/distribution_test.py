from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TestCase
from django.test import override_settings
from django.test.client import RequestFactory
from tabulate import tabulate

from distributions.views import automatic
from general_view import get_grouptype
from timeline.models import TimeSlot, TimePhase


@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
                   TESTING=True)
class AutomaticDistributionTest(TestCase):
    """
    Class with testclient to test views. Some functions to setup data in the database.
    """

    def setUp(self):
        """
        Setup test data, like users and groups.
        """
        self.factory = RequestFactory()

        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', settings.BASE_DIR + '/../testdb/testdb-anonymous-3.json', verbosity=0)

    def test_distribution(self):
        n = datetime.now().date()
        g = get_grouptype('3')
        u = get_user_model().objects.filter(groups=g)
        for ts in TimeSlot.objects.all():  # two years of testdata
            print('year: {} (id: {})'.format(ts.Name, ts.pk))
            ts.Begin = n - timedelta(days=2)
            ts.End = n + timedelta(days=2)
            ts.save()
            assert not ts.timephases.exists(), 'there should be no timephases.'
            tp = TimePhase(
                Timeslot=ts,
                Begin=n - timedelta(days=2),
                End=n + timedelta(days=2),
                Description=4,
            )
            tp.save()
            for t in [1, 2]:
                print("automatic distribution type {}".format(t))
                request = self.factory.get('/distributions/automatic/{}/'.format(t))
                request.user = u.first()  # any support user will do.
                response = automatic(request, t)
                print("Percentage division per cohort. random and preference 1-5")
                print(tabulate(response[1], headers=response[0]))
            # prevent interference with other timeslot
            ts.Begin = n + timedelta(days=4)
            ts.End = n + timedelta(days=8)
            ts.save()
