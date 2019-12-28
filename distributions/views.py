#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models import Q, F
from django.http import HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from htmlmin.decorators import not_minified_response

from index.decorators import group_required
from timeline.decorators import phase_required
from general_form import ConfirmForm
from general_mail import EmailThreadTemplate
from general_model import print_list
from general_view import get_all_students, get_all_staff
from proposals.models import Proposal
from proposals.utils import get_all_proposals, get_share_link, get_cached_project
from students.models import Application, Distribution
from students.views import get_all_applications
from support.exports import get_list_distributions_xlsx
from timeline.utils import get_timeslot, get_timephase_number
from . import distribution
from .forms import AutomaticDistributionOptionForm

warningString = 'Something failed in the server, please refresh this page (F5) or contact system administrator'


@group_required("type3staff", "type6staff")
def list_applications_distributions(request):
    """
    Show a list of all active proposals with the applications and possibly distributions of students.
    Used for support staff as an overview.
    Same table include as in manual distribute
    """
    if get_timephase_number() < 3:
        raise PermissionDenied("There are no applications or distributions yet.")
    elif get_timephase_number() > 5:
        projects = get_all_proposals().filter(Q(Status=4) & Q(distributions__isnull=False)).distinct()
        projects = projects.select_related('ResponsibleStaff', 'Track').prefetch_related('Assistants',
                                                                                         'Private',
                                                                                         'distributions__Application',
                                                                                         'distributions__Student__usermeta')

    else:  # phase 3 & 4 & 5
        projects = get_all_proposals().filter(Status=4)
        projects = projects.select_related('ResponsibleStaff', 'Track').prefetch_related('Assistants',
                                                                                         'Private',
                                                                                         'applications__Student__usermeta',
                                                                                         'distributions__Application',
                                                                                         'distributions__Student__usermeta')

    return render(request, 'distributions/list_applications_distributions.html', {"proposals": projects})


@not_minified_response
@group_required("type3staff", "type6staff")
def list_distributions_xlsx(request):
    """
    Same as supportListApplications but as XLSX
    """
    if get_timephase_number() < 3:
        raise PermissionDenied("There are no applications yet")
    elif get_timephase_number() > 4:
        projects = get_all_proposals().filter(Q(Status=4) & Q(distributions__isnull=False)).distinct()
    else:
        projects = get_all_proposals().filter(Status=4)
    # projects = projects.select_related('ResponsibleStaff', 'Track').prefetch_related('Assistants',
    #                                                                                  'distributions__Student__usermeta')
    file = get_list_distributions_xlsx(projects)
    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename=marketplace-projects-distributions.xlsx'
    return response


@group_required('type3staff')
def manual(request):
    """
    Support page to distribute students manually to projects. Uses ajax calls to change distributions.
    Same table included as in list appls/dists

    :param request:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 6:
        raise PermissionDenied('Distribution is not possible in this timephase')

    props = get_all_proposals().filter(Q(Status__exact=4)) \
        .select_related('ResponsibleStaff__usermeta', 'Track', 'TimeSlot') \
        .prefetch_related('Assistants__usermeta', 'Private__usermeta', 'applications__Student__usermeta',
                          'distributions__Student__usermeta')
    # includes students without applications.
    # also show undistributed in phase 6
    studs = get_all_students(undistributed=True).exclude(distributions__TimeSlot=get_timeslot()) \
        .select_related('usermeta') \
        .prefetch_related('applications__Proposal').distinct()
    dists = Distribution.objects.filter(TimeSlot=get_timeslot()) \
        .select_related('Student__usermeta', 'Proposal', 'Application__Student__usermeta')
    return render(request, 'distributions/manual_distribute.html', {'proposals': props,
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
        except User.DoesNotExist:
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (User cannot be found)'})
        if student.distributions.filter(TimeSlot=get_timeslot()).exists():
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (Student already distributed)'})
        try:
            dist = Distribution()
            dist.Student = student
            dist.Proposal = get_cached_project(request.POST['propTo'])
            # check whether there was an application
            try:
                dist.Application = get_all_applications(dist.Student).get(Proposal=dist.Proposal)
                appl_prio = dist.Application.Priority
            except Application.DoesNotExist:
                appl_prio = -1
                dist.Application = None
            dist.TimeSlot = get_timeslot()
            dist.full_clean()
            dist.save()
        except Exception as e:
            return JsonResponse({'type': 'warning', 'txt': warningString, 'exception': str(e)})
        return JsonResponse({'type': 'success', 'txt': 'Distributed Student ' + dist.Student.usermeta.get_nice_name() +
                                                       ' to Proposal ' + dist.Proposal.Title, 'prio': appl_prio})
    else:
        raise PermissionDenied("You don't know what you're doing!")


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
        except User.DoesNotExist:
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (User cannot be found)'})
        try:
            dist = student.distributions.get(TimeSlot=get_timeslot())
        except Distribution.DoesNotExist:
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (Distribution cannot be found)'})
        try:
            n = dist.delete()
            if n[0] == 1:
                return JsonResponse(
                    {'type': 'success', 'txt': 'Undistributed Student ' + dist.Student.usermeta.get_nice_name()})
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
        except User.DoesNotExist:
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (User cannot be found)'})
        try:
            dist = student.distributions.get(TimeSlot=get_timeslot())
        except Distribution.DoesNotExist:
            return JsonResponse({'type': 'warning', 'txt': warningString + ' (Distribution cannot be found)'})
        try:
            # change Proposal
            dist.Proposal = get_cached_project(request.POST['propTo'])
            # change Application if user has Application
            try:
                dist.Application = get_all_applications(dist.Student).get(Proposal=dist.Proposal)
                appl_prio = dist.Application.Priority
            except Application.DoesNotExist:
                dist.Application = None
                appl_prio = -1
            dist.full_clean()
            dist.save()
        except Exception as e:
            return JsonResponse({'type': 'warning', 'txt': warningString, 'exception': str(e)})
        return JsonResponse(
            {'type': 'success', 'txt': 'Changed distributed Student ' + dist.Student.usermeta.get_nice_name() +
                                       ' to Proposal ' + dist.Proposal.Title, 'prio': appl_prio})
    else:
        raise PermissionDenied("You don't know what you're doing!")


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
            ts = get_timeslot()
            # iterate through projects, put students directly in the mail list
            for prop in get_all_proposals().filter(Q(distributions__isnull=False)):
                for dist in prop.distributions.filter(TimeSlot=ts):
                    mails.append({
                        'template': 'email/studentdistribution.html',
                        'email': dist.Student.email,
                        'subject': 'distribution',
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
                        'subject': 'distribution',
                        'context': {
                            'supervisor': usr,
                            'projects': usr.proposals.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })
                if usr.proposalsresponsible.filter(TimeSlot=get_timeslot()).exists():
                    mails.append({
                        'template': 'email/supervisordistribution.html',
                        'email': usr.email,
                        'subject': 'distribution',
                        'context': {
                            'supervisor': usr,
                            'projects': usr.proposalsresponsible.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })

            # UNCOMMENT THIS TO MAIL NOT_DISTRIBUTED STUDENTS WITH 'action required'
            # for usr in get_all_students().filter(distributions__isnull=True):
            #     mails.append({
            #         'template': 'email/studentnodistribution.html',
            #         'email': usr.email,
            #         'subject': 'action required',
            #         'context': {
            #             'student': usr,
            #         }
            #     })
            EmailThreadTemplate(mails).start()

            return render(request, 'support/email_progress.html')
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm mailing distributions',
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def automatic_options(request):
    """
    Option frontend for automatic() distribution

    :param request:
    :return: 302 to automatic() with correct get options
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:  # 4 or 5
        raise PermissionDenied('Distribution is not possible in this timephase')

    if request.method == 'POST':
        form = AutomaticDistributionOptionForm(request.POST)
        if form.is_valid():
            # redirect to automatic
            distribution_type = form.cleaned_data['distribution_type']
            print(distribution_type)
            distribute_random = form.cleaned_data['distribute_random']
            automotive_preference = form.cleaned_data['automotive_preference']
            return HttpResponseRedirect(reverse('distributions:distributeproposaloption',
                                                kwargs={'dist_type': distribution_type,
                                                        'distribute_random': distribute_random,
                                                        'automotive_preference': automotive_preference}
                                                ))
    else:
        form = AutomaticDistributionOptionForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Automatic distribution options',
        'buttontext': 'View result'
    })


@group_required('type3staff')
def automatic(request, dist_type, distribute_random=1, automotive_preference=1):
    """
    After automatic distribution, this pages shows how good the automatic distribution is. At this point a type3staff
     member can choose to apply the distributions. Later, this distribution can be edited using manual distributions.

    :param request:
    :param dist_type: which type automatic distribution is used.
    :param distribute_random: Whether to distribute leftover students to random projects
    :param automotive_preference: Distribute automotive students first to automotive people
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:  # 4 or 5
        raise PermissionDenied('Distribution is not possible in this timephase')

    if int(dist_type) == 1:
        typename = 'calculated by student'
    elif int(dist_type) == 2:
        typename = 'calculated by project'
    else:
        raise PermissionDenied("Invalid type")

    if distribute_random not in [0, 1]:
        raise PermissionDenied("Invalid option type random")
    if automotive_preference not in [0, 1]:
        raise PermissionDenied("Invalid option type automotive")

    dists = []  # list to store actual user and proposal objects, instead of just ID's like distobjs.
    if request.method == 'POST':
        jsondata = request.POST.get('jsondata', None)
        if jsondata is None:
            return render(request, 'base.html', {'Message': 'Invalid POST data'})
        distobjs = json.loads(jsondata)  # json blob with all dists with studentID projectID and preference
        for obj in distobjs:
            dists.append({
                'student': User.objects.get(pk=obj['StudentID']),
                'proposal': get_all_proposals().get(pk=obj['ProjectID']),
                'preference': obj['Preference'],
            })

        form = ConfirmForm(request.POST)
        if form.is_valid():
            # delete all old distributions of this timeslot
            Distribution.objects.filter(TimeSlot=get_timeslot()).delete()
            # save the stuff
            for dist in dists:
                dstdbobj = Distribution()
                dstdbobj.Student = dist['student']
                dstdbobj.Proposal = dist['proposal']
                dstdbobj.TimeSlot = get_timeslot()
                if dist['preference'] > 0:
                    try:
                        dstdbobj.Application = \
                            Application.objects.filter(Q(Student=dist['student']) &
                                                       Q(Proposal=dist['proposal']) &
                                                       Q(Priority=dist['preference']) &
                                                       Q(Proposal__TimeSlot=get_timeslot()))[0]
                    except Application.DoesNotExist:
                        dstdbobj.Application = None
                else:
                    dstdbobj.Application = None
                dstdbobj.save()

            return render(request, 'base.html', {
                'Message': 'Distributions saved!',
                'return': 'distributions:SupportListApplicationsDistributions',
            })

    else:
        # Handle the most common errors beforehand with a nice message
        error_list = ''
        stds = get_all_students().filter(personal_proposal__isnull=False, personal_proposal__TimeSlot=get_timeslot()).distinct().prefetch_related('personal_proposal')
        for u in stds:  # all private students
            ps = u.personal_proposal.filter(TimeSlot=get_timeslot())
            if ps.count() > 1:  # more than one private proposal.
                error_list += "<li>User {} has multiple private proposals ({}). Please resolve this!</li>" \
                    .format(u, print_list(ps))
            if ps.first().Status != 4:
                error_list += "<li>User {} has private proposals which is not yet public. Please upgrade proposal {} to public!</li>" \
                    .format(u, ps.first())
        if error_list:
            return render(request, 'base.html', {
                'Message': '<h1>Automatic distribution cannot start</h1><p>The following error(s) occurred:</p><ul>{}</ul>'
                          .format(error_list),
                'return': 'distributions:SupportListApplicationsDistributions',
            })

        form = ConfirmForm()
        # run the algorithms
        # catch any remaining errors of the algorithm with a broad exception exception.
        try:
            if int(dist_type) == 1:  # from student
                distobjs = distribution.calculate_1_from_student(
                    distribute_random=distribute_random,
                    automotive_preference=automotive_preference)
            elif int(dist_type) == 2:  # from project
                distobjs = distribution.calculate_2_from_project(
                    distribute_random=distribute_random,
                    automotive_preference=automotive_preference)
        # invalid types are catched at the begin of the function
        except Exception as e:
            return render(request, "base.html", {
                'Message': '<h1>Automatic distribution cannot start</h1><p>The following error(s) occurred:</p>{}'
                          .format(e)})

    # convert to django models from db
    # and make scatter chart data
    scatter = []
    undistributed = list(get_all_students())  # get all students and remove all distributed students later.
    for obj in distobjs:  # distobjs is saved as json blob in the view, to use later on for distributions.
        student = get_all_students().get(pk=obj.StudentID)
        undistributed.remove(student)  # remove distributed student from undistributed students list.
        scatter.append({  # data for scatterplot ECTS vs Preference
            'x': student.usermeta.ECTS,
            'y': obj.Preference,
        })
        try:
            proposal = get_all_proposals().get(pk=obj.ProjectID)
        except Proposal.DoesNotExist:
            raise Exception("Proposal id {} cannot be found in all_proposals!".format(obj.ProjectID))
        dists.append({
            'student': student,
            'proposal': proposal,
            'preference': obj.Preference,
        })
    # show undistributed students also in the table. (Not added to json blob)
    for obj in undistributed:
        dists.append({
            'student': obj,
            'proposal': None,
            'preference': 'Not distributed. ' + ('With' if obj.applications.filter(Proposal__TimeSlot=get_timeslot()).exists() else 'No') + ' applications.',
        })

    cohorts = distribution.get_cohorts()

    # make headers for table and find cohort for each student.
    columns = ['Total']
    # calculate stats per cohort
    prefs = {  # first column with total
        'Total': [obj['preference'] for obj in dists if obj['proposal'] is not None],
    }
    for c in cohorts:  # all next columns in table for each cohort. First column is totals.
        columns.append(c)
        prefs[c] = []
        for obj in dists:
            if obj['proposal'] is not None:  # do not count not-distributed students in the stats.
                if obj['student'].usermeta.Cohort == int(c):
                    prefs[c].append(obj['preference'])  # list of all individual preferences in this cohort

    # make a table
    table = []
    pref_options = list(range(-1, settings.MAX_NUM_APPLICATIONS + 1))  # all options for preference.
    for pref in pref_options:  # each preference, each row.
        # set first column
        if pref == -1:  # random distributed students.
            this_row = ['Random']
        elif pref == 0:
            this_row = ['Private']  # private proposals
        else:
            this_row = ['#' + str(pref), ]  # application preference
        # set other columns
        for c in columns:  # add columns to the row.
            num = prefs[c].count(pref)
            try:
                this_row.append('{}% ({})'.format(round(num / len(prefs[c]) * 100), num))
            except ZeroDivisionError:
                this_row.append('{}% ({})'.format(0, 0))

        # add row the the table
        table.append(this_row)
    # one but last row with totals.
    this_row = ['Total Distributed']
    for c in columns:
        this_row.append(len(prefs[c]))
    table.append(this_row)

    # last row with undistributed.
    this_row = ['Not Distributed', len(undistributed)]
    for c in columns[1:]:  # skip total column, is already added.
        this_row.append(len([u for u in undistributed if u.usermeta.Cohort == c]))
    table.append(this_row)

    # show the tables for testing.
    if settings.TESTING:
        return columns, table, dists

    data = [obj.as_json() for obj in distobjs]
    return render(request, 'distributions/automatic_distribute.html', {
        'typename': typename,
        'distributions': dists,
        'form': form,
        'stats': table,
        'stats_header': columns,
        'scatter': scatter,
        'jsondata': json.dumps(data),
        'distribute_random': distribute_random,
        'automotive_preference': automotive_preference,
    })


@group_required('type3staff')
@phase_required(4, 5, 6)
def list_second_choice(request):
    """
    list all students with a random distribution, without project and all non-full projects

    :param request:
    :return:
    """

    props = get_all_proposals().filter(Status=4, Private__isnull=True).distinct().annotate(num_distr=Count('distributions')).filter(TimeSlot=get_timeslot(),
                                                                               num_distr__lt=F('NumStudentsMax')).order_by('Title')
    prop_obj = [[prop, get_share_link(prop.pk)] for prop in props]
    no_dist = get_all_students(undistributed=True).filter(distributions__isnull=True, applications__isnull=False).distinct()
    # filter students in this year with only applications in other year
    no_dist = [s for s in no_dist if s.applications.filter(Proposal__TimeSlot=get_timeslot()).exists()]

    return render(request, 'distributions/list_second_choice.html', {
        'distributions': Distribution.objects.filter(TimeSlot=get_timeslot(),
                                                     Application__isnull=True,
                                                     Proposal__Private__isnull=True).order_by('Student'),
        'no_dist': no_dist,
        'proposals': prop_obj,

    })


@group_required('type3staff')
@phase_required(4, 5, 6)
def delete_random_distributions(request):
    """
    Delete all distributions who have had a random assigned project

    :param request:
    :return:
    """
    dists = Distribution.objects.filter(TimeSlot=get_timeslot(),
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

    return render(request, 'distributions/delete_random_dists.html', {
        'form': form,
        'buttontext': 'Confirm',
        'formtitle': 'Confirm deletion distributions of random assigned projects',
        'distributions': dists,
    })
