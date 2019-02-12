from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.db.models import Q
from django.test import TestCase
from django.test import override_settings
from django.test.client import RequestFactory
from tabulate import tabulate

from distributions.views import automatic
from general_view import get_grouptype
from timeline.models import TimeSlot, TimePhase


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

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
        management.call_command('loaddata', settings.BASE_DIR + '/distributions/distribution-testdb.json', verbosity=0)
        self.debug = True # whether to produce output

    def test_distribution(self):
        n = datetime.now().date()
        g = get_grouptype('3')
        u = get_user_model().objects.filter(groups=g)
        for ts in TimeSlot.objects.all():  # two years of testdata
            year_all = get_user_model().objects.filter(Q(usermeta__EnrolledBEP=True) & Q(groups=None) & Q(usermeta__TimeSlot=ts))
            year_priv = year_all.filter(Q(personal_proposal__isnull=False)).distinct().count()  # private students of this year.
            year_norm = len([s for s in year_all.filter(Q(personal_proposal__isnull=True) & Q(applications__isnull=False)).distinct() if s.applications.filter(Proposal__TimeSlot=ts).exists()])  # all students without private with applications. These can be distributed.
            year_all = year_all.count()  # all students in this year
            if self.debug:
                print(color.BOLD + color.UNDERLINE + 'year: {} (id: {}). {} students, {} privates and {} normal applications.'.format(ts.Name, ts.pk, year_all, year_priv, year_norm) + color.END)
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
            for distribute_random in [0, 1]:
                if self.debug:
                    print(color.BOLD + "With distribute random {}".format(bool(distribute_random)) + color.END)
                for automotive_preference in [0, 1]:
                    if self.debug:
                        print(color.BOLD + "With automotive preference {}".format(bool(automotive_preference)) + color.END)
                    for t in [1, 2]:
                        if self.debug:
                            print(color.BOLD + "automatic distribution type {}".format(['', 'From student', 'From project'][t]) + color.END)
                        request = self.factory.get('/distributions/automatic/{}/'.format(t))
                        request.user = u.first()  # any support user will do.
                        headers, table, dists = automatic(request, t, distribute_random, automotive_preference)
                        if self.debug:
                            print("Percentage division per cohort. random and preference 1-5")
                            print(tabulate(table, headers=headers))
                        # dists, response[2] dict:
                        # 'student': student,
                        # 'proposal': get_all_proposals().get(pk=obj.ProjectID),
                        # 'preference': obj.Preference,
                        # find overfull projects
                        proposals = set([d['proposal'] for d in dists if d['proposal'] is not None])
                        for p in proposals:
                            proposal_min = p.NumStudentsMin
                            proposal_max = p.NumStudentsMax
                            distributed = [d for d in dists if d['proposal'] == p]
                            proposal_dists = len(distributed)
                            priv = list(p.Private.all())
                            if self.debug:
                                if proposal_dists > proposal_max:
                                    print("Prop {} has {} dists where {} is max!".format(p, proposal_dists,
                                                                                         proposal_max))
                                    for d in distributed:
                                        if priv:
                                            print(' - prop: {}, private: {}, student: {}'.format(d['proposal'].id, priv,
                                                                                                 d['student'].id))
                                        else:
                                            print(' - prop: {}, student: {}'.format(d['proposal'].id, d['student'].id))
                                # find underfull projects
                                if proposal_dists < proposal_min:
                                    print("Prop {} has {} dists where {} is min!".format(p, proposal_dists,
                                                                                         proposal_min))
                                    for d in distributed:
                                        if priv:
                                            print(' - prop: {}, private: {}, student: {}'.format(d['proposal'].id, priv, d['student'].id))
                                        else:
                                            print(' - prop: {}, student: {}'.format(d['proposal'].id, d['student'].id))
                        students = [d['student'] for d in dists]
                        dupes = set([x for x in students if students.count(x) > 1])
                        if dupes:
                            print("Duplicate distributed students:")
                            for s in dupes:
                                print('- {}'.format(s))
                            raise AssertionError('Duplicate distributions found!')
                        # check distribution of private students, only check count in total column.
                        assert table[1][1].split(' ')[-1] == "({})".format(year_priv), 'Not all private students are distributed!'
                        # check correctness of random distribute
                        if not distribute_random:
                            # first row of table is list with all random dists count. Should be all zero if not random distribute.
                            # prevent interference with other timeslot
                            assert all([table[0][i] == "0% (0)" for i in range(1, len(table[0]) - 1)]), 'Random persons distributed while distribute random is false!'
                        else:
                            # if all random students are distributed, everyone with applications or private should have a project
                            assert int(table[-2][1]) == year_norm+year_priv, 'Not all privates or normal students with applications are distributed. This can only be correct if all projects are filled to max (undercapacity).'
                        # check count of total is equal to number of students in this year
                        assert int(table[-2][1])+int(table[-1][1]) == year_all, 'Sum of number of distruted and not distributed students is not equal to number of students in this year!'
            ts.Begin = n + timedelta(days=4)
            ts.End = n + timedelta(days=8)
            ts.save()
