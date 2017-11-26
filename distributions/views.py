import json
from datetime import datetime

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from BepMarketplace.decorators import group_required
from general_form import ConfirmForm
from general_mail import EmailThreadMultipleTemplate
from general_view import get_all_students, get_timeslot, get_timephase_number, get_all_staff, get_all_proposals
from proposals.cacheprop import getProp
from students.models import Application, Distribution
from timeline.models import TimeSlot
from . import distribution

warningString = "Something failed in the server, please refresh this page (F5) or contact system administrator"


@group_required("type3staff")
def supportDistributeApplications(request):
    """
    Support page to distribute students manually to projects. Uses ajax calls to change distributions.

    :param request:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        raise PermissionDenied("Distribution is not possible in this timephase")

    props = get_all_proposals().filter(Q(Status__exact=4))
    studs = get_all_students().filter(Q(distributions=None))
    dists = Distribution.objects.filter(Timeslot=get_timeslot())
    return render(request, "distributions/distributeApplications.html", {"proposals": props, "undistributedStudents": studs, "distributions": dists})


@group_required("type3staff")
def distributeApi(request):
    """
    AJAX call from manual distribute to distribute

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        raise PermissionDenied("Distribution is not possible in this timephase")

    if request.method == 'POST':
        try:
            student = get_all_students().get(pk=request.POST["student"])
            if student.distributions.filter(Timeslot=get_timeslot()).exists():
                return HttpResponse('{"type":"warning","txt":"' + warningString + ' (Student already distributed)"}')
            dist = Distribution()
            dist.Student = student
            dist.Proposal = getProp(request.POST["propTo"])
            # check whether there was an application
            applprio = -1
            if dist.Student.applications.count() > 0:
                if dist.Student.applications.filter(Proposal=dist.Proposal).count() > 0:
                    appl = dist.Student.applications.get(Proposal=dist.Proposal)
                    applprio = appl.Priority
                else:
                    appl=None
            else:
                appl = None
            dist.Application = appl
            dist.Timeslot = get_timeslot()
            dist.full_clean()
            dist.save()
        except Exception as e:
            return HttpResponse('{"type":"warning","txt":"' + warningString + '","exception":"' + str(e) + '"}')
        returnval = {"type":"success", "txt":'Distributed Student '+ dist.Student.get_full_name() + ' to Proposal ' + dist.Proposal.Title, "prio":applprio}
        return HttpResponse(json.dumps(returnval))
    else:
        raise PermissionDenied("You don't know what you're doing!")


@group_required("type3staff")
def undistributeApi(request):
    """
    AJAX call from manual distribute to undistribute

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        raise PermissionDenied("Distribution is not possible in this timephase")

    if request.method == 'POST':
        try:
            student = get_all_students().get(pk=request.POST["student"])
            dist = student.distributions.get(Timeslot=get_timeslot())
            n = dist.delete()
            if n[0] == 1:
                return HttpResponse(
                    '{"type":"success","txt":"Undistributed Student ' + dist.Student.get_full_name() +'"}')
            else:
                return HttpResponse('{"type":"warning","txt":"'+warningString+' (distributions not deleted)"}')
        except Exception as e:
            return HttpResponse('{"type":"warning","txt":"'+warningString+'","exception":"'+str(e)+'"}')
    else:
        raise PermissionDenied("You don't know what you're doing!")


@group_required("type3staff")
def changeDistributeApi(request):
    """
    AJAX call from manual distribute to change a distribution

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        raise PermissionDenied("Distribution is not possible in this timephase")

    if request.method == 'POST':
        try:
            student = get_all_students().get(pk=request.POST["student"])
            dist = student.distributions.get(Timeslot=get_timeslot())
            # change Proposal
            dist.Proposal = getProp(request.POST["propTo"])
            # change Application if user has Application
            applprio = -1
            if dist.Student.applications.count() > 0:
                if dist.Student.applications.filter(Proposal=dist.Proposal).count() > 0:
                    appl = dist.Student.applications.get(Proposal=dist.Proposal)
                    applprio = appl.Priority
                else:
                    appl=None
            else:
                appl = None
            dist.Application = appl
            dist.full_clean()
            dist.save()
        except Exception as e:
            return HttpResponse('{"type":"warning","txt":"' + warningString + '","exception":"' + str(e) + '"}')
        returnval = {"type":"success", "txt":'Changed distributed Student '+ dist.Student.get_full_name() +' to Proposal '+dist.Proposal.Title,"prio":applprio}
        return HttpResponse(json.dumps(returnval))
    else:
        raise PermissionDenied("You don't know what you're doing!")


@group_required('type3staff')
def mailDistributions(request):
    """
    Mail all distributions to affected users

    :param request:
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        # mailing is possible in phase 4 or 5
        raise PermissionDenied("Mailing distributions is not possible in this timephase")

    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            mails = []
            ts = TimeSlot.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))
            # iterate through projects, put students directly in the mail list
            for prop in get_all_proposals().filter(Q(distributions__isnull=False)):
                for dist in prop.distributions.filter(Timeslot=ts):
                    mails.append({
                        'template'  : 'email/studentdistribution.html',
                        'email'     : dist.Student.email,
                        'subject'   : 'BEP Marketplace Distribution',
                        'context'   : {
                            'project' : prop,
                            'student' : dist.Student,
                        }
                    })

            # iterate through all supervisors
            for usr in get_all_staff().filter(Q(groups__name='type1staff') | Q(groups__name='type2staff')):
                if usr.proposals.count() > 0:
                    mails.append({
                        'template'  : 'email/assistantdistribution.html',
                        'email'     : usr.email,
                        'subject'   : 'BEP Marketplace Distribution',
                        'context'   : {
                            'supervisor' : usr,
                            'projects'   : usr.proposals.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })
                if usr.proposalsresponsible.count() > 0:
                    mails.append({
                        'template'  : 'email/supervisordistribution.html',
                        'email'     : usr.email,
                        'subject'   : 'BEP Marketplace Distribution',
                        'context'   : {
                            'supervisor': usr,
                            'projects': usr.proposalsresponsible.filter(TimeSlot=get_timeslot()).distinct(),
                        }
                    })

            # iterate all students and find those with no distributions
            for usr in get_all_students().filter(distributions__isnull=True):
                mails.append({
                    'template'  : 'email/studentnodistribution.html',
                    'email'     : usr.email,
                    'subject'   : 'BEP Marketplace Action Required',
                    'context'   : {
                        'student' : usr,
                    }
                })
            EmailThreadMultipleTemplate(mails).start()

            return render(request, "support/emailProgress.html")
    else:
        form = ConfirmForm()

    return render(request, "GenericForm.html", {
        "form" : form,
        "formtitle" : "Confirm mailing distributions",
        "buttontext" : "Confirm"
    })


@group_required('type3staff')
def proposalOfDistribution(request, dtype):
    """
    After automatic distribution, this pages shows how good the automatic distribution is. At this point a type3staff
     member can choose to apply the distributions. Later, this distribution can be edited using manual distributions.

    :param request:
    :param dtype: which type automatic distribution is used.
    :return:
    """
    if get_timephase_number() < 4 or get_timephase_number() > 5:
        raise PermissionDenied("Distribution is not possible in this timephase")

    dists = []
    if request.method == "POST":
        jsondata = request.POST.get('jsondata', None)
        if jsondata is None:
            return render(request, 'base.html', {'Message': 'Invalid POST data'})
        distobjs = json.loads(jsondata)
        for obj in distobjs:
            dists.append({
                'student': get_all_students().get(pk=obj['StudentID']),
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
                        Application.objects.filter(Q(Student=dist['student']) & Q(Proposal=dist['proposal']) \
                                                   & Q(Priority=dist['preference']))[0]
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
        if int(dtype) == 1:
            distobjs = distribution.CalculateFromStudent()
        elif int(dtype) == 2:
            distobjs = distribution.CalculateFromProjects()
        else:
            return render(request, 'base.html', {'Message': 'invalid type'})
        # convert to django models from db
        for obj in distobjs:
            dists.append({
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
    cohorts = distribution.getAllCohorts()

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
        typename = 'Calculated old way'
    elif int(dtype) == 2:
        typename = 'Calculated new way'
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