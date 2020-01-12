#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
General functions/classes used in tests.
"""

import re
import sys
import traceback
from datetime import datetime, timedelta

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_module

from index.models import UserMeta, UserAcceptedTerms, Track
from presentations.models import PresentationOptions, PresentationTimeSlot, PresentationSet, Room
from proposals.models import Proposal
from results.models import ResultOptions
from students.models import Distribution
from support.models import GroupAdministratorThrough, CapacityGroup
from timeline.models import TimeSlot, TimePhase
from django.conf import settings
from general_view import get_timephase_number

TEST_HTML_VALID = False
#
# if TEST_HTML_VALID:
#     from htmlvalidator.client import ValidatingClient

# disable cache for all tests
@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}},
                   EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH='./test_mail.log',
                   MIDDLEWARE_CLASSES=[mc for mc in settings.MIDDLEWARE
                                       if mc != 'tracking.middleware.TelemetryMiddleware'],
)
# @override_settings(
#                 HTMLVALIDATOR_ENABLED = True,  # to test html valid
#                 # HTMLVALIDATOR_DUMPDIR = 'validationerrors/',  # default it /tmp
#                 HTMLVALIDATOR_OUTPUT = 'stdout',  # default is 'file'
#                 HTMLVALIDATOR_VNU_URL = 'http://localhost:8888/',
#                 HTMLVALIDATOR_FAILFAST = True,
#                )
class ViewsTest(TestCase):
    """
    Class with testclient to test views. Some functions to setup data in the database.
    """

    def setUp(self):
        """
        Setup test data, like users and groups.
        """
        # whether to produce output, please override this on app level if debug is required.
        self.debug = False

        # to test that each page is at least tested once, check if all urls of the app are tested.
        urlpatterns = import_module(self.app + '.urls', 'urlpatterns').urlpatterns
        self.allurls = [x.name for x in urlpatterns]

        # the client used for testing
        if TEST_HTML_VALID:
            self.client = ValidatingClient()
        else:
            self.client = Client()
        # info string to show debug info in case of test assertion failure
        self.info = {}

        # The timeslot used for testing proposal of current timeslot
        self.ts = TimeSlot(Begin=datetime.now(), End=datetime.now() + timedelta(days=3), Name='thisyear')
        self.ts.save()

        # The timephase used for testing. The Description is changed every test.
        self.tp = TimePhase(Begin=datetime.now(), End=datetime.now() + timedelta(days=3), TimeSlot=self.ts,
                            Description=1)
        self.tp.save()

        # The timeslot used for testing proposal of next timeslot
        self.nts = TimeSlot(Begin=datetime.now() + timedelta(days=5), End=datetime.now() + timedelta(days=8),
                            Name='nextyear')
        self.nts.save()

        # The timeslot used for testing proposal of previous timeslot
        self.pts = TimeSlot(Begin=datetime.now() - timedelta(days=5), End=datetime.now() - timedelta(days=3),
                            Name='prevyear')
        self.pts.save()

        # Create capacity groups models
        groups = (
            ("EES", "Electrical Energy Systems"),
            ("ECO", "Electro-Optical Communications"),
            ("EPE", "Electromechanics and Power Electronics"),
            ("ES", "Electronic Systems"),
            ("IC", "Integrated Circuits"),
            ("CS", "Control Systems"),
            ("SPS", "Signal Processing Systems"),
            ("PHI", "Photonic Integration"),
            ("EM", "Electromagnetics")
        )

        for group in groups:
            self.c, created = CapacityGroup.objects.get_or_create(ShortName=group[0], FullName=group[1])
            assert created

        # Create groups and users
        self.create_groups()
        self.create_users()

        # Track for automotive, with trackhead t-h. Automotive track must exist because it is special. (distributions)
        th = User.objects.get(username='t-h')
        self.track = Track(Name='Automotive', ShortName='AU', Head=th)
        self.track.save()

        grt = User.objects.get(username='t-4')
        grr = User.objects.get(username='r-4')
        # only read/write administration is tested. Not readonly.
        g = GroupAdministratorThrough(User=grt, Super=True,
                                      Group=CapacityGroup.objects.all()[0])
        g.save()
        g2 = GroupAdministratorThrough(User=grr, Super=True,
                                       Group=CapacityGroup.objects.all()[1])
        g2.save()

        ## setup matrix with all possible rights
        # expected results:
        # r=random, t=this(for this proposal)
        # s=student, p=private-student, r=responsible, a=assistant, u=assistant_not_verified t=trackhead
        # ta = assessor of presentation, 4=groupadministration, 5=studyadvisor, 6=profskill
        # matrix with different types of permissions, set for each user of the array self.usernames
        # permissions by user. The order is the order of self.usernames. User 'god' is disabled (not tested).
                #  usernames:    r-1  t-1  r-h  t-h  r-2  t-2  t-u  r-3  r-s  t-p  r-4  t-4  r-5  r-6  ra-1  ta-1  sup, ano
        self.p_forbidden =      [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 302]  # no one
        self.p_superuser =      [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 302]  # no one
        self.p_all =            [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 302]  # everyone
        self.p_anonymous =      [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200]  # everyone
        self.p_redirect =       [302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302, 302]  # everyone

        self.p_staff =          [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 200, 200, 200, 200, 200, 200, 200, 302]  # all staff, general
        self.p_staff_veri =     [200, 200, 200, 200, 200, 200, 403, 200, 403, 403, 200, 200, 200, 200, 200, 200, 200, 302]  # all staff, without unverified
        self.p_staff122u35 =    [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 403, 403, 200, 403, 200, 200, 200, 302]  # all staff, for chooseedit list
        self.p_staff_prop =     [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 200, 200, 403, 403, 200, 200, 200, 302]  # all staff, to create proposals
        self.p_staff_prop_no4 = [200, 200, 200, 200, 200, 200, 200, 200, 403, 403, 403, 403, 403, 403, 200, 200, 200, 302]  # all staff to create but no type4
        self.p_staff_prop_nou=  [200, 200, 200, 200, 200, 200, 403, 200, 403, 403, 200, 200, 403, 403, 200, 200, 200, 302]  # all staff, to create proposals, no unverified
        self.p_staff_stud =     [200, 200, 200, 200, 200, 200, 403, 200, 403, 403, 403, 403, 403, 200, 200, 200, 200, 302]  # all staff that can see students (1,2,3,6)

        self.p_all_this =       [403, 200, 403, 200, 403, 200, 200, 200, 403, 403, 403, 200, 403, 403, 403, 403, 200, 302]  # staff of this proposal
        self.p_all_this_pres=   [403, 200, 403, 200, 403, 200, 200, 200, 403, 403, 403, 200, 403, 403, 403, 200, 200, 302]  # staff of this proposal including ta-1
        self.p_all_this_dist=   [403, 200, 403, 200, 403, 200, 403, 200, 200, 403, 403, 403, 403, 200, 403, 403, 200, 302]  # staff of this proposal, as distributed to r-s (not t-p!) and assessor. Also type6.
        self.p_all_this_dist_ta=[403, 200, 403, 200, 403, 200, 403, 200, 200, 403, 403, 403, 403, 200, 403, 200, 200, 302]  # staff of this proposal, as distributed to r-s (not t-p!) and assessor. Also type6. and assessor
        self.p_no_assistant =   [403, 200, 403, 200, 403, 403, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 200, 302]  # staff of this proposal except assistants. For up/downgrading and edit proposal.
        self.p_staff_prv_results=[403, 200, 403, 200, 403, 200, 403, 200, 403, 403, 403, 403, 403, 403, 403, 403, 200, 302]  # staff of this proposal except assistants including assessors. For results staff grading form, without assessor.
        self.p_staff_results =  [403, 200, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 200, 200, 302]  # staff of this proposal except assistants including assessors. For results staff grading form.
        self.p_all_this_view =  [403, 200, 403, 200, 403, 200, 200, 200, 403, 403, 403, 200, 403, 403, 403, 403, 200, 302]  # staff of this proposal including view only users (type4)

        self.p_private =        [403, 200, 403, 200, 403, 200, 200, 200, 403, 200, 403, 200, 403, 403, 403, 403, 200, 302]  # private proposal view status 4
        self.p_private_pres=    [403, 200, 403, 200, 403, 200, 200, 200, 403, 200, 403, 200, 403, 403, 403, 200, 200, 302]  # private proposal view status 4, in phase 7 or if presentation is public.
        self.p_trackhead =      [403, 403, 403, 200, 403, 403, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 200, 302]  # trackhead of proposal and support
        self.p_grade_final =    [403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 200, 302]  # Trackhead and assessor can finalize grades.
        self.p_grade_staff =    [403, 200, 403, 200, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 200, 200, 302]  # staff of this proposal except assistants, for grading
        self.p_track =          [403, 403, 200, 200, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 302]  # any trackhead
        self.p_pending =        [200, 200, 200, 200, 200, 200, 200, 403, 403, 403, 200, 200, 403, 403, 200, 200, 200, 302]  # staff with pending proposals

        self.p_support      =   [403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 403, 200, 302]  # type3 support
        self.p_support_prv  =   [403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 200, 403, 403, 200, 302]  # 3+6

        self.p_cgadmin      =   [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 200, 403, 403, 403, 403, 200, 302]  # type4 (not superuser)
        # self.p_study        =   [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 200, 302]  # type5
        self.p_prv =            [403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 200, 302]  # 6

        self.p_student =        [403, 403, 403, 403, 403, 403, 403, 403, 200, 200, 403, 403, 403, 403, 403, 403, 403, 302]  # any student
        self.p_studentnotpriv=  [403, 403, 403, 403, 403, 403, 403, 403, 200, 403, 403, 403, 403, 403, 403, 403, 403, 302]  # student without private proposal

        self.p_download_share=  [404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 403]  # used to test filesdownload (with sharelink proposals)
        self.p_404 =            [404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 404, 302]  # used to test filesdownload


    def create_groups(self):
        """
        Create all groups for the system.

        :param self:
        :return:
        """
        # setup all groups
        self.group_names = [
            'type1staff',  # project responsible
            'type2staff',  # project assistant
            'type2staffunverified',  # unverified assistant
            'type3staff',  # support staff
            'type4staff',  # Capacity group administration
            'type5staff',  # Study advisor
            'type6staff',  # Prof skill administration
        ]
        for g in self.group_names:
            group, created = Group.objects.get_or_create(name=g)
            assert created
            # make group object accessable as a class variable. < self.type1staff > etc.
            setattr(self, g, group)

    def create_users(self):
        """
        Takes self.usernames and creates users based on this. The last character of the username determnines the group
        WARNING: This only generates users and assign groups.
        It does not assign roles (like groupadministration and trackhead models).
        """
        # create testusers using the naming-patern: [r t]-[s p 1 2 u 3 t ]
        # r=random (any person of the given type), t=this(for this project)
        # 1=type1, 2=type2, 3=type3, s=Student, u=Unverified-type2, h=track-Head, p=Private-student
        self.usernames = [
            'r-1',  # responsible staff
            't-1',  # responsible staff
            'r-h',  # responsible staff, trackhead
            't-h',  # responsible staff, trackhead
            'r-2',  # assistant
            't-2',  # assistant
            't-u',  # unverified assistant
            'r-3',  # support staff
            'r-s',  # student without private proposal
            't-p',  # student with private proposal
            'r-4',  # Capacity group administration of other group than tested proposal
            't-4',  # Capacity group administration of group of tested proposal
            'r-5',  # Study advisor
            'r-6',  # Prof skill administration
            'ra-1',  # type1 and assessor of other project
            'ta-1',  # type1 and assessor of project
            'sup',  # god user (superuser)
            'ano',  # anonymous user
        ]
        # Create the users and assign groups/roles.
        self.users = {}
        for n in self.usernames:
            if n != 'ano':
                u = User(username=n)
                u.email = n + '@' + settings.STAFF_EMAIL_DOMAINS[0]
                u.save()
                x = n.split('-')[-1]
                if x == '1':
                    u.groups.add(self.type1staff)
                elif x == 'h':  # trackhead
                    u.groups.add(self.type1staff)
                elif x == '2':
                    u.groups.add(self.type2staff)
                elif x == 'u':
                    u.groups.add(self.type2staffunverified)
                elif x == '3':
                    u.groups.add(self.type3staff)
                elif x == '4':
                    u.groups.add(self.type4staff)
                elif x == '5':
                    u.groups.add(self.type5staff)
                elif x == '6':
                    u.groups.add(self.type6staff)
                elif n == 'sup':
                    u.groups.add(self.type3staff)
                    u.is_superuser = True
                    u.is_staff = True
                else:  # student
                    u.email = n + '@' + settings.STUDENT_EMAIL_DOMAINS[0]
                u.save()
                self.users[n] = u
                m = UserMeta(User=u,
                             EnrolledBEP=True, )
                m.save()
                m.TimeSlot.add(self.ts)
                m.save()
                ua = UserAcceptedTerms(User=u)
                ua.save()

    def links_in_view_test(self, sourceurl, skip=[]):
        """
        Find all links in a response and check if they return status 200.

        :param sourceurl: the page which is parsed to test the links on the page.
        :param skip: urls to not test
        :return:
        """
        for user in self.users.values():
            if self.debug:
                print(user)
            if (user.username == 't-u' or user.username == 'r-u') and \
                    self.tp.Description > 3:
                # ignore unverfied assistants in later timephases
                continue
            if (user.username == 't-p' or user.username == 't-s') and \
                    self.tp.Description < 3:
                # ignore students in first timephases
                continue
            self.client.force_login(user)
            self.proposal.Status = 4
            self.privateproposal.Status = 4
            self.status = 4
            self.proposal.save()
            self.privateproposal.save()

            self.view_test_status(sourceurl, 200)
            response = self.client.get(sourceurl)
            urls = re.findall('/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+/',
                              str(response.content))
            urls = [x for x in urls if (">" not in x
                                        and "<" not in x
                                        and "//" not in x
                                        and "/static/" not in x
                                        and "/logout/" not in x
                                        and "tracking/live/" not in x
                                        and "tracking/viewnumber/" not in x
                                        and "js_error_hook" not in x
                                        and x not in skip)]
            for link in urls:  # select the url in href for all a tags(links)
                if link in skip:
                    continue
                if self.debug:
                    print('url: {}'.format(link))
                self.proposal.Status = 4
                self.privateproposal.Status = 4
                self.status = 4
                self.proposal.save()
                self.privateproposal.save()
                self.info['user'] = user.username
                self.view_test_status(link, 200)

            self.client.logout()

    def loop_phase_code_user(self, phases, codes):
        """
        Loop over the given phases and test with all codes

        :param phases:
        :param codes: list of views and expected status codes
        :return:
        """
        assert isinstance(phases, list) or isinstance(phases, range)
        for phase in phases:
            if phase != get_timephase_number():
                if phase == -1:
                    self.tp.Begin = datetime.now() + timedelta(days=1)
                    self.tp.save()
                    self.info['phase'] = 'No Phase'
                else:
                    self.tp.Begin = datetime.now()
                    self.tp.Description = phase
                    self.tp.save()
                    self.info['phase'] = str(phase)
            if self.debug:
                print("Testing phase {}".format(phase))
            self.loop_code_user(codes)

    def loop_code_user(self, codes):
        """
        Test all views for all users

        :param codes: list of views and expected status codes
        :return:
        """
        for page, status in codes:
            if self.debug:
                self.info['reverse'] = str(page)
                self.info['statuscodes'] = status
            view = self.app + ":" + page[0]
            if any(isinstance(i, list) for i in status):
                # we're dealing with proposals status tests here
                ProjectViewsTestGeneral.loop_user_status(self, view, status, page[1])
            else:
                # normal test without proposals
                self.loop_user(view, status, page[1])
            # remove the page from the list of urls of this app.
            if page[0] in self.allurls: self.allurls.remove(page[0])

    def loop_user(self, view, status, kw=None):
        """
        Loop over the provided pages with status code for each user and test these.

        :param view: name of the page, for reverse view
        :param status: array of http status that is expected for each user
        :param kw: keyword args for the given view.
        :return:
        """
        for i, username in enumerate(self.usernames):
            self.info['user'] = username
            self.info['kw'] = kw
            if self.debug:
                self.info['user-index'] = i
            # log the user in
            if username != 'ano':
                u = User.objects.get(username=username)
                if self.debug:
                    self.info['user-groups'] = u.groups.all()
                    self.info['user-issuper'] = u.is_superuser
                self.client.force_login(u)
            self.view_test_status(reverse(view, kwargs=kw), status[i])
            if username != 'ano':
                self.client.logout()

    def view_test_status(self, link, expected):
        """
        Test a given view

        :param self: the instance for the testcase class, containing self.client, the testclient instance.
        :param link: a link to a view to test
        :param expected: the expected response code
        :return:
        """
        try:
            response = self.client.get(link)
            response_code = response.status_code
            if response_code == 403 or expected == 403:
                try:
                    exception = list(response.context[0])[0]["exception"]
                except:
                    try:
                        exception = list(response.context[0])[0]["Message"]
                    except:
                        # exception = response.context  # this is a large amount of information
                        exception = 'Reason not found in context!'
                self.info['exception'] = exception
            else:
                if response_code == 404:
                    for d in response.context.dicts:
                        try:
                            self.info['exception'] = d['Message']
                            break
                        except:
                            continue
                else:
                    self.info['exception'] = "no 403"
        except Exception as e:
            response_code = 500
            print("Error: {}".format(e))
            self.info['exception'] = '500'
            traceback.print_exc(file=sys.stdout)

        self.assertEqual(response_code, expected,
                         msg='Expected status code {} but got {} for {} info: {}.'
                         .format(expected, response_code, link, self.info))


class ProjectViewsTestGeneral(ViewsTest):
    """
    Functions to test pages related to proposals/projects
    """

    def setUp(self):
        """
        Initialization test data for proposals/projects

        :param self: self
        :return:
        """
        # create users and groups in parent function
        super(ProjectViewsTestGeneral, self).setUp()

        # Random track head r-h
        rth = User.objects.get(username='r-h')
        rt = Track(Name='Smart Sustainable', ShortName='SSS', Head=rth)
        rt.save()

        # The proposal used for testing
        self.proposal = Proposal(Title="testproposal",
                                 ResponsibleStaff=self.users.get('t-1'),
                                 Group=CapacityGroup.objects.all()[0],
                                 NumStudentsMin=1,
                                 NumStudentsMax=1,
                                 GeneralDescription="Test general description",
                                 StudentsTaskDescription="Test student task description",
                                 Status=1,
                                 Track=self.track,
                                 TimeSlot=self.ts,
                                 )
        self.proposal.save()
        self.p = self.proposal.id
        self.proposal.Assistants.add(self.users.get('t-2'))
        self.proposal.Assistants.add(self.users.get('t-u'))
        self.proposal.save()
        # make private proposal
        self.privateproposal = Proposal(Title="privateproposaltest",
                                        ResponsibleStaff=self.users.get('t-1'),
                                        Group=CapacityGroup.objects.all()[0],
                                        NumStudentsMin=1,
                                        NumStudentsMax=1,
                                        GeneralDescription="Test general description",
                                        StudentsTaskDescription="Test student task description",
                                        Status=1,
                                        Track=self.track,
                                        TimeSlot=self.ts,
                                        )

        self.privateproposal.save()
        self.ppriv = self.privateproposal.id
        self.privateproposal.Assistants.add(self.users.get('t-2'))
        self.privateproposal.Assistants.add(self.users.get('t-u'))
        self.privateproposal.Private.add(self.users.get('t-p'))
        self.privateproposal.save()

        # make a distribution, this gets id 1.
        self.distribution_random = Distribution(
            Proposal=self.proposal,
            Student=self.users['r-s'],  # assign the student without private proposal
            TimeSlot=self.ts,
        )
        self.distribution_random.save()
        dp = Distribution(
            Proposal=self.privateproposal,
            Student=self.users['t-p'],  # assign the student with private proposal
            TimeSlot=self.ts,
        )
        dp.save()
        self.results_options = ResultOptions(
            TimeSlot=self.ts
        )
        self.results_options.save()

        po = PresentationOptions(
            TimeSlot=self.ts,
        )
        po.save()

        r = Room(
            Name='Test-room',

        )
        r.save()
        # one presentation set with two presentationtimeslots. ta-1 is assessor of the set.
        p = PresentationSet(
            PresentationOptions=po,
            PresentationRoom=r,
            AssessmentRoom=r,
            DateTime=timezone.now(),
        )
        p.save()
        p.Assessors.add(self.users['ta-1'])
        # presentation timeslot student r
        ptsr = PresentationTimeSlot(
            Presentations=p,
            Distribution=self.distribution_random,
            DateTime=timezone.now() + timedelta(hours=2)
        )
        ptsr.save()
        # presentation timeslot student p
        ptsp = PresentationTimeSlot(
            Presentations=p,
            Distribution=dp,
            DateTime=timezone.now() + timedelta(hours=3)
        )
        ptsp.save()

    def loop_user_status(self, view, status, kw=None):
        """
        Test all users and proposal status for a given page. Called from self.all_pages_test()

        :param view: name of the page, for reverse view
        :param status: array of http status that is expected for each user
        :param kw: keyword args for the given view.
        :return:
        """
        assert isinstance(status, list)
        for i, username in enumerate(self.usernames):
            self.info['user'] = username
            self.info['kw'] = kw
            if self.debug:
                self.info['user-index'] = i
            if username != 'ano':
                # log the user in
                u = User.objects.get(username=username)
                if self.debug:
                    self.info['user-groups'] = u.groups.all()
                    self.info['user-issuper'] = u.is_superuser
                self.client.force_login(u)
            # check for each given status from the status-array
            l = len(status)
            for status0 in range(0, l):
                self.status = status0 + 1
                self.info['status'] = self.status
                # Expected response code
                expected = status[status0][i]
                # Reset the project status, because it changes after a test call to upgrade/downgrade
                self.proposal.Status = self.status
                self.proposal.save()
                self.privateproposal.Status = self.status
                self.privateproposal.save()
                self.view_test_status(reverse(view, kwargs=kw), expected)
            # user logout
            if username != 'ano':
                self.client.logout()
