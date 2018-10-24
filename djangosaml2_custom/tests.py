from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from djangosaml2_custom.views import check_user
from general_test import ProjectViewsTestGeneral
from index.models import UserMeta

class DjangoSaml2CustomTest(ProjectViewsTestGeneral):
    def setUp(self):
        self.app = 'djangosaml2_custom'
        super(DjangoSaml2CustomTest, self).setUp()
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.phases = [-1, 1, 2, 3, 4, 5, 6, 7]
        self.student_usernames = ['r-s', 't-p']

        # set osiris data to osiris.csv
        with open('osiris.csv', 'w') as f:
            f.truncate()
            f.write(
                "email;IDNR-BEP;enrolled;extension;cohort;ects;automotive;\nt-p@student.tue.nl;0000000;1;0;2018;125;0;\nr-s@student.tue.nl;0000001;1;0;2018;125;0;")
            f.flush()

    def test_login(self):
        link = '/login/'
        request = self.factory.get(link)
        for username, user in self.users.items():
            for phase in self.phases:
                self.tp.Description = phase
                self.tp.save()
                self.info['phase'] = str(phase)

                # check login for this user in this phase
                response = check_user(request, user)
                if username in self.student_usernames:
                    # student login allowed in phase 3 and larger. Phase 5, 6, 7 only allowed with distribution
                    if phase > 2:
                        assert response is True, 'student allowed to login in timephase 3 and later.'
                        assert self.ts in user.usermeta.TimeSlot.all(), 'student timeslot updated to current timeslot.'
                    else:
                        assert response.status_code == 403, 'student login forbidden in phase 1 and 2.'
                elif username == 'sup':
                    assert '2FA' in str(response.content), 'support users should have 2FA explanation in error message.'
                else:
                    # support staff, always allowed when valid timephase
                    assert response is True, 'staff users should be able to login using SAML'

        # check no timephase
        self.tp.delete()
        for username, user in self.users.items():
            # check login for this user in this phase
            response = check_user(request, user)
            if username in self.student_usernames:
                assert response.status_code == 403, 'student login forbidden when no timephase.'
            elif username == 'sup':
                assert '2FA' in str(response.content), 'support users should have 2FA explanation in error message.'
            else:  # no timephase is tested for correct behavior, so login is allowed when no timephase.
                assert response is True, 'users should be able to login using SAML when no timephase'

        # check no timeslot, set to previous timeslot
        self.ts.Begin = datetime.now() + timedelta(days=1)
        self.ts.save()
        for username, user in self.users.items():
            # check login for this user in this phase
            response = check_user(request, user)
            if username in self.student_usernames:
                assert response.status_code == 403, 'student login forbidden when no timeslot.'
            elif username == 'sup':
                assert '2FA' in str(response.content), 'support users should have 2FA explanation in error message.'
            elif self.type3staff in user.groups.all():
                assert response is True, 'support users should be able to login using SAML when no timeslot'
            else:
                assert response.status_code == 403, 'regular staff is not allowed when no timslot'

    def test_add_unverified(self):
        """
        Test if new staff users are given the type2staffunverified group
        :return:
        """
        link = '/login/'
        request = self.factory.get(link)

        user = User(username='newstaff', email='newstaff@' + settings.STAFF_EMAIL_DOMAINS[0])
        user.save()
        # generate meta, normally done in pre_user_save signal in handlers.py.
        meta = UserMeta(User=user)
        meta.save()
        response = check_user(request, user)
        assert self.type2staffunverified in user.groups.all()
        assert response is True
