import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Count
from django.http import JsonResponse
from django.shortcuts import render

from BepMarketplace.decorators import group_required, phase_required
from general_form import ConfirmForm
from general_mail import EmailThreadMultipleTemplate
from general_view import get_all_students, get_all_staff
from proposals.models import Proposal
from proposals.utils import get_all_proposals, get_share_link, get_cached_project
from students.models import Application, Distribution
from students.views import get_all_applications
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number
from . import distribution

warningString = 'Something failed in the server, please refresh this page (F5) or contact system administrator'


@group_required('type3staff')
def manual(request):
    """
    Support page to distribute students manually to projects. Uses ajax calls to change distributions.

    :param request:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 6:
        raise PermissionDenied('Distribution is not possible in this timephase')

    props = get_all_proposals().filter(Q(Status__exact=4))
    studs = get_all_students(undistributed=True).filter(Q(distributions=None))  # also show undistributed in phase 6
    dists = Distribution.objects.filter(Timeslot=get_timeslot())
    return render(request, 'distributions/distributeApplications.html', {'proposals': props,
                                                                         'undistributedStudents': studs,
                                                                         'distributions': dists,
                                                                         'hide_sidebar': True})


@group_required('type3staff')
def api_distribute(request):
    """
    AJAX call from manual distribute to distribute

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 6:
        raise PermissionDenied('Distribution is not possible in this timephase')

    if request.method == 'POST':
        try:
            student = get_all_students(undistributed=True).get(pk=request.POST['student'])
            if student.distributions.filter(Timeslot=get_timeslot()).exists():
                return JsonResponse({'type': 'warning', 'txt': warningString + ' (Student already distributed)'})
            dist = Distribution()
            dist.Student = student
            dist.Proposal = get_cached_project(request.POST['propTo'])
            # check whether there was an application
            try:
                dist.Application = get_all_applications(dist.Student).get(Proposal=dist.Proposal)
                applprio = dist.Application.Priority
            except:
                applprio = -1
                dist.Application = None
            dist.Timeslot = get_timeslot()
            dist.full_clean()
            dist.save()
        except Exception as e:
            return JsonResponse({'type': 'warning', 'txt': warningString, 'exception': str(e)})
        return JsonResponse({'type': 'success', 'txt': 'Distributed Student ' + dist.Student.get_full_name() +
                                                       ' to Proposal ' + dist.Proposal.Title, 'prio': applprio})
    else:
        raise PermissionDenied('You don\'t know what you\'re doing!')


@group_required('type3staff')
def api_undistribute(request):
    """
    AJAX call from manual distribute to undistribute

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        # Not in phase 6, because projects already started.
        raise PermissionDenied('Undistribution is not possible in this timephase')

    if request.method == 'POST':
        try:
            student = get_all_students(undistributed=True).get(pk=request.POST['student'])
            dist = student.distributions.get(Timeslot=get_timeslot())
            n = dist.delete()
            if n[0] == 1:
                return JsonResponse(
                    {'type': 'success', 'txt': 'Undistributed Student ' + dist.Student.get_full_name()})
            else:
                return JsonResponse({'type': 'warning', 'txt': warningString + ' (distributions not deleted)'})
        except Exception as e:
            return JsonResponse({'type': 'warning', 'txt': warningString, 'exception': str(e)})
    else:
        raise PermissionDenied('You don\'t know what you\'re doing!')


@group_required('type3staff')
def api_redistribute(request):
    """
    AJAX call from manual distribute to change a distribution

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 6:
        raise PermissionDenied('Distribution is not possible in this timephase')

    if request.method == 'POST':
        try:
            student = get_all_students(undistributed=True).get(pk=request.POST['student'])
            dist = student.distributions.get(Timeslot=get_timeslot())
            # change Proposal
            dist.Proposal = get_cached_project(request.POST['propTo'])
            # change Application if user has Application
            try:
                dist.Application = get_all_applications(dist.Student).get(Proposal=dist.Proposal)
                applprio = dist.Application.Priority
            except:
                dist.Application = None
                applprio = -1
            dist.full_clean()
            dist.save()
        except Exception as e:
            return JsonResponse({'type': 'warning', 'txt': warningString, 'exception': str(e)})
        return JsonResponse({'type': 'success', 'txt': 'Changed distributed Student ' + dist.Student.get_full_name() +
                                                       ' to Proposal ' + dist.Proposal.Title, 'prio': applprio})
    else:
        raise PermissionDenied('You don\'t know what you\'re doing!')


@group_required('type3staff')
def mail_distributions(request):
    """
    Mail all distributions to affected users

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        # mailing is possible in phase 4 or 5
        raise PermissionDenied('Mailing distributions is not possible in this timephase')

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            mails = []
            ts = TimeSlot.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))
            # iterate through projects, put students directly in the mail list
            for prop in get_all_proposals().filter(Q(distributions__isnull=False)):
                for dist in prop.distributions.filter(Timeslot=ts):
                    mails.append({
                        'template': 'email/studentdistribution.html',
                        'email': dist.Student.email,
                        'subject': 'BEP Marketplace Distribution',
                        'context': {
                            'project': prop,
                            'student': dist.Student,
                        }
                    })

            # iterate through all assistants and responsible
            for usr in get_all_staff().filter(Q(groups__name='type1staff') | Q(groups__name='type2staff')):
                if usr.proposals.filter(TimeSlot=get_timeslot()).exists():
                    mails.append({
                        'template': 'email/assistantdistribution.html',
                        'email': usr.email,
                        'subject': 'BEP Marketplace Distribution',
                        'context': {
                            'supervisor': usr,
                            'projects': usr.proposals.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })
                if usr.proposalsresponsible.filter(TimeSlot=get_timeslot()).exists():
                    mails.append({
                        'template': 'email/supervisordistribution.html',
                        'email': usr.email,
                        'subject': 'BEP Marketplace Distribution',
                        'context': {
                            'supervisor': usr,
                            'projects': usr.proposalsresponsible.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })

            # UNCOMMENT THIS TO MAIL NOT_DISTRIBUTED STUDENTS WITH 'action required'
            # iterate all students and find those with no distributions
            # for usr in get_all_students().filter(distributions__isnull=True):
            #     mails.append({
            #         'template': 'email/studentnodistribution.html',
            #         'email': usr.email,
            #         'subject': 'BEP Marketplace Action Required',
            #         'context': {
            #             'student': usr,
            #         }
            #     })
            EmailThreadMultipleTemplate(mails).start()

            return render(request, 'support/emailProgress.html')
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm mailing distributions',
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def automatic(request, dtype):
    """
    After automatic distribution, this pages shows how good the automatic distribution is. At this point a type3staff
     member can choose to apply the distributions. Later, this distribution can be edited using manual distributions.

    :param request:
    :param dtype: which type automatic distribution is used.
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:  # 4 or 5
        raise PermissionDenied('Distribution is not possible in this timephase')

    dists = []
    if request.method == 'POST':
        jsondata = request.POST.get('jsondata', None)
        if jsondata is None:
            return render(request, 'base.html', {'Message': 'Invalid POST data'})
        distobjs = json.loads(jsondata)
        for obj in distobjs:
            dists.append({
                'student': User.objects.get(pk=obj['StudentID']),
                'proposal': get_all_proposals().get(pk=obj['ProjectID']),
                'preference': obj['Preference'],
            })

        form = ConfirmForm(request.POST)
        if form.is_valid():
            # delete all old distributions of this timeslot
            Distribution.objects.filter(Timeslot=get_timeslot()).delete()
            # save the stuff
            for dist in dists:
                dstdbobj = Distribution()
                dstdbobj.Student = dist['student']
                dstdbobj.Proposal = dist['proposal']
                dstdbobj.Timeslot = get_timeslot()
                if dist['preference'] > 0:
                    try:
                        dstdbobj.Application = \
                            Application.objects.filter(Q(Student=dist['student']) &
                                                       Q(Proposal=dist['proposal']) &
                                                       Q(Priority=dist['preference']) &
                                                       Q(Proposal__TimeSlot=get_timeslot()))[0]
                    except:
                        dstdbobj.Application = None
                else:
                    dstdbobj.Application = None
                dstdbobj.save()

            return render(request, 'base.html', {
                'Message': 'Distributions saved!',
                'return': 'support:SupportListApplicationsDistributions',
            })

    else:
        form = ConfirmForm()
        # run the algorithms
        if int(dtype) == 1:  # from student
            distobjs = distribution.CalculateFromStudent()
        elif int(dtype) == 2:  # from project
            distobjs = distribution.CalculateFromProjects()
        else:
            return render(request, 'base.html', {'Message': 'invalid type'})
        # convert to django models from db
        for obj in distobjs:
            dists.append({
                # this will fail if a student does not have a timeslot, which should not happen.
                'student': get_all_students().get(pk=obj.StudentID),
                'proposal': get_all_proposals().get(pk=obj.ProjectID),
                'preference': obj.Preference,
            })

    # calculate stats
    prefs = {
        'total': [x['preference'] for x in dists],
    }
    stats = {
        'total': []
    }
    cohorts = distribution.get_cohorts()

    for c in cohorts:
        stats[c] = []
        prefs[c] = []

    for c in cohorts:
        for obj in dists:
            if obj['student'].usermeta.Cohort == int(c):
                prefs[c].append(obj['preference'])

    for n in range(0, settings.MAX_NUM_APPLICATIONS + 1):
        for k in stats.keys():
            try:
                stats[k].append(round((prefs[k].count(n) / len(prefs[k])) * 100))
            except:
                stats[k].append(0)

    if int(dtype) == 1:
        typename = 'Calculated by student'
    elif int(dtype) == 2:
        typename = 'Calculated calculated by project'
    else:
        typename = 'invalid'

    data = [obj.as_json() for obj in distobjs]
    return render(request, 'distributions/distributionProposal.html', {
        'typename': typename,
        'distributions': dists,
        'form': form,
        'stats': stats,
        'jsondata': json.dumps(data),
    })


@group_required('type3staff')
@phase_required(4, 5, 6)
def list_second_choice(request):
    """
    list all students with a random distribution

    :param request:
    :return:
    """
    props = Proposal.objects.annotate(num_distr=Count('distributions')).filter(TimeSlot=get_timeslot()
                                                                               , num_distr__lt=F(
            'NumstudentsMax')).order_by('Title')
    sharelinks = [get_share_link(request, x.pk) for x in props]

    return render(request, 'distributions/secondChoiseList.html', {
        'distributions': Distribution.objects.filter(Timeslot=get_timeslot(),
                                                     Application__isnull=True,
                                                     Proposal__Private__isnull=True).order_by('Student'),
        'proposals': props,
        'sharelinks': sharelinks,
    })


@group_required('type3staff')
@phase_required(4, 5, 6)
def delete_random_distributions(request):
    """
    Delete all distributions who have had a random assigned project

    :param request:
    :return:
    """
    dists = Distribution.objects.filter(Timeslot=get_timeslot(),
                                        Application__isnull=True,
                                        Proposal__Private__isnull=True).order_by('Student')
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            dists.delete()
            return render(request, 'base.html', {
                'Message': 'Distributions deleted!'
            })
    else:
        form = ConfirmForm()

    return render(request, 'distributions/deleterandomdists.html', {
        'form': form,
        'buttontext': 'Confirm',
        'formtitle': 'Confirm deletion distributions of random assigned projects',
        'distributions': dists,
    })
