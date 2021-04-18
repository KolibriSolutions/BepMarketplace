#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import zipfile
from datetime import datetime
from io import BytesIO
from os import path

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from htmlmin.decorators import not_minified_response

from distributions.utils import get_distributions
from general_model import delete_object
from general_model import get_ext
from general_view import get_grouptype
from index.decorators import student_only, group_required
from professionalskills.decorators import can_access_professionalskills
from professionalskills.models import StudentFile
from proposals.decorators import can_view_project
from proposals.models import Proposal
from proposals.utils import get_cached_project
from results.models import GradeCategory, CategoryResult
from students.decorators import can_apply
from students.models import Distribution
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number, get_recent_timeslots
from tracking.models import ApplicationTracking
from .exports import get_list_students_xlsx
from professionalskills.forms import StudentFileForm
from .models import Application
from .utils import get_all_applications


@student_only()
def list_applications(request):
    """
    List the applications of a student, with a button to retract the application

    :param request:
    """
    applications = {}
    tss = set(list(request.user.applications.all().values_list('Proposal__TimeSlot', flat=True).distinct()) + \
              list(request.user.personal_proposal.all().values_list('TimeSlot', flat=True).distinct()))
    for ts in tss:
        tsn = TimeSlot.objects.filter(pk=ts).first() or 'Future'
        applications[tsn] = [get_all_applications(request.user, timeslot=ts), request.user.personal_proposal.filter(TimeSlot=ts)]

    return render(request, 'students/list_applications.html', context={
        'tss': tss,
        'applications': applications,
        'num_app': settings.MAX_NUM_APPLICATIONS,
    })


@can_apply
def prio_up(request, application_id):
    """
    Increase the priority of an application of a student.

    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
    if not targetapp.Proposal.cur_or_future():
        return render(request, 'base.html', context={
            'Message': 'Old applications cannot be changed.',
            'return': 'students:listapplications',
        })
    if targetapp.Student != request.user:
        return render(request, 'base.html', context={
            'Message': 'You are not the owner of this application!',
            'return': 'students:listapplications',
        })
    if targetapp.Priority == 1:
        return render(request, 'base.html', context={
            'Message': 'Already at top priority',
            'return': 'students:listapplications',
        })
    swappapp = get_all_applications(request.user, timeslot=targetapp.Proposal.TimeSlot).filter(Q(Priority=targetapp.Priority - 1))[0]
    swappapp.Priority += 1
    targetapp.Priority -= 1
    swappapp.save()
    targetapp.save()
    return redirect('students:listapplications')


@can_apply
def prio_down(request, application_id):
    """
    Decrease the priority of an application of a student.

    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
    if not targetapp.Proposal.cur_or_future():
        return render(request, 'base.html', context={
            'Message': 'Old applications cannot be changed.',
            'return': 'students:listapplications',
        })
    if targetapp.Student != request.user:
        return render(request, 'base.html', context={
            'Message': 'You are not the owner of this application!',
            'return': 'students:listapplications',
        })
    if targetapp.Priority == settings.MAX_NUM_APPLICATIONS:
        return render(request, 'base.html', context={
            'Message': 'Already at bottom priority',
            'return': 'students:listapplications',
        })
    apps = get_all_applications(request.user, timeslot=targetapp.Proposal.TimeSlot).filter(Q(Priority=targetapp.Priority + 1))
    if len(apps) == 0:
        return render(request, 'base.html', context={
            'Message': 'Already at bottom priority',
            'return': 'students:listapplications',
        })
    swappapp = apps[0]
    swappapp.Priority -= 1
    targetapp.Priority += 1
    swappapp.save()
    targetapp.save()
    return redirect('students:listapplications')


@can_apply
def retract_application(request, application_id):
    """
    Let a user un-apply / retract an application.
    Also possible for projects of other year and non-active projects. To be able to remove false applications.

    :param request:
    :param application_id: Application id
    """
    appl = get_object_or_404(Application, pk=application_id)
    if not appl.Proposal.cur_or_future():
        return render(request, 'base.html', context={
            'Message': 'Old applications cannot be changed.',
            'return': 'students:listapplications',
        })
    track = ApplicationTracking()
    track.Proposal = appl.Proposal
    track.Student = request.user
    track.Type = 'r'
    track.save()

    for app in get_all_applications(request.user, timeslot=appl.Proposal.TimeSlot):
        if app.Priority > appl.Priority:
            app.Priority -= 1
            app.save()
    delete_object(appl)
    return render(request, 'base.html', context={
        'Message': 'Deleted application',
        'return': 'students:listapplications',
    })


@can_view_project
@can_apply
def apply(request, pk):
    """
    Let a user apply to a proposal. Called after confirmapply.

    :param request:
    :param pk: id of a proposal.
    """
    prop = get_cached_project(pk)
    if prop.Status < 4:
        raise PermissionDenied('This proposal is not public, application is not possible.')

    if get_all_applications(request.user, timeslot=prop.TimeSlot).count() >= settings.MAX_NUM_APPLICATIONS:
        return render(request, 'base.html', context={
            'Message': 'already at max amount of applied proposals<br>'
                       'retract one first before continuing',
            'return': 'students:listapplications',
        })
    if get_all_applications(request.user, timeslot=prop.TimeSlot).filter(Q(Proposal=prop)).exists():
        return render(request, 'base.html', context={
            'Message': 'You already applied to this proposal.',
            'return': 'students:listapplications',
        })

    track = ApplicationTracking()
    track.Proposal = prop
    track.Student = request.user
    track.Type = 'a'
    track.save()

    appl = Application()
    appl.Proposal = prop
    highestprio = get_all_applications(request.user, timeslot=prop.TimeSlot).aggregate(Max('Priority'))['Priority__max']
    appl.Student = request.user
    if highestprio is None:
        appl.Priority = 1
    else:
        appl.Priority = highestprio + 1
    appl.save()
    return render(request, 'base.html', context={
        'Message': 'Application saved with priority number {}'.format(appl.Priority),
        'return': 'students:listapplications',
    })


@can_view_project
@can_apply
def confirm_apply(request, pk):
    """
    After a student presses apply on a proposal, he/she has to confirm the application on this page.
    This page also checks whether the user is allowed to apply

    :param request:
    :param pk: id of the proposal
    """
    prop = get_cached_project(pk)
    if prop.Status < 4:
        raise PermissionDenied('This proposal is not public, application is not possible.')

    if get_all_applications(request.user, timeslot=prop.TimeSlot).filter(Q(Proposal=prop)).exists():
        return render(request, 'base.html', context={
            'Message': 'You already applied to this proposal.',
            'return': 'students:listapplications',
        })
    return render(request, 'students/apply.html', context={
        'proposal': get_object_or_404(Proposal, pk=pk),
    })


@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def list_students(request, timeslot):
    """
    For support staff, responsibles and assistants to view their students.
    List all students with distributions that the current user is allowed to see.
    Including a button to view the students files.
    Shows the grades as well.

    :param request:
    :param timeslot: the timeslot to look at. None for current timeslot (Future distributions do not exist)
    :return:
    """
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    if ts.Begin > timezone.now().date():
        raise PermissionDenied("Future students are not yet known.")
    if ts == get_timeslot():
        current_ts = True
    else:
        current_ts = False
    show_grades = False
    if current_ts:
        # for current timeslot, check time phases.
        if get_timephase_number() < 0:  # no timephase
            if get_timeslot() is None:  # no timeslot
                raise PermissionDenied("System is closed.")
        else:
            if get_timephase_number() < 4:
                raise PermissionDenied("Students are not yet distributed")
            if get_timephase_number() < 5 and not get_grouptype("3") in request.user.groups.all():
                return render(request, "base.html", {'Message':
                                                         "When the phase 'Distribution of projects' is finished, you can view your students here."})
        if get_timephase_number() == -1 or get_timephase_number() >= 6:  # also show grades when timeslot but no timephase.
            show_grades = True
    else:  # historic grades
        show_grades = True

    des = get_distributions(request.user, ts).select_related('Proposal__ResponsibleStaff',
                                                             'Proposal__Track',
                                                             'Student__usermeta').prefetch_related(
        'Proposal__Assistants', 'files__staffresponse')
    cats = None

    if show_grades:
        cats = GradeCategory.objects.filter(TimeSlot=ts)
        des.prefetch_related('results__Category')
    deslist = []
    # make grades
    for d in des:
        reslist = []
        if show_grades:
            for c in cats:
                try:
                    reslist.append(d.results.get(Category=c).Grade)
                except CategoryResult.DoesNotExist:
                    reslist.append('-')
        deslist.append([d, reslist])
    return render(request, "students/list_students.html", {'des': deslist,
                                                           'typ': cats,
                                                           'show_grades': show_grades,
                                                           'hide_sidebar': True,
                                                           'timeslots': get_recent_timeslots(),
                                                           'timeslot': ts,
                                                           'is_current': current_ts,
                                                           })


@not_minified_response
@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def list_students_xlsx(request, timeslot):
    """
    Same as liststudents but as XLSX. The combination of students and grades is done in general_excel.

    :param request:
    :param timeslot: pk of timeslot to download
    """
    timeslot = get_object_or_404(TimeSlot, pk=timeslot)
    if timeslot == get_timeslot():  # current ts
        if get_timephase_number() < 0:
            if get_timeslot() is None:
                raise PermissionDenied("System is closed.")
        else:
            if get_timephase_number() < 4:
                raise PermissionDenied("Students are not yet distributed")
            if get_timephase_number() < 5 and not get_grouptype("3") in request.user.groups.all():
                return render(request, "base.html", {'Message':
                                                         "When the phase 'Distribution of projects is "
                                                         "finished, you can view your students here."})
    elif timeslot.End > datetime.now().date():  # future ts.
        raise PermissionDenied('Future timeslot.')
    typ = GradeCategory.objects.filter(TimeSlot=timeslot)
    des = get_distributions(request.user, timeslot=timeslot)
    file = get_list_students_xlsx(des, typ, timeslot=timeslot)

    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = f'attachment; filename=students {timeslot}.xlsx'
    return response


@not_minified_response
@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def download_files(request, timeslot):
    """
    all student files of PRV of timeslot

    :param request:
    :param timeslot: timeslot id.
    :return:
    """
    timeslot = get_object_or_404(TimeSlot, pk=timeslot)
    if timeslot == get_timeslot():  # current year
        if 4 > get_timephase_number() >= 0:  # only in phase 4, 5, 6 and 7 (although 4 is not useful)
            raise PermissionDenied("This page is not available in the current time phase.")
    elif timeslot.End > datetime.now().date():  # future ts.
        raise PermissionDenied('Future timeslot.')

    in_memory = BytesIO()
    des = get_distributions(request.user, timeslot=timeslot)
    if not des:
        return render(request, 'base.html', context={'Message': 'You do not have students.', 'return': 'students:liststudents', 'returnget': timeslot.pk})
    empty = True
    with zipfile.ZipFile(in_memory, 'w') as archive:
        for d in des:
            files = d.files.all()
            for file in files:
                empty = False
                try:
                    with open(file.File.path, 'rb') as fstream:
                        name, ext = path.splitext(file.OriginalName)
                        name = path.basename(truncatechars(name, 25))
                        ext = get_ext(file.File.name)
                        archive.writestr('{}-({})/{}/{}-{}.{}'.format(d.Student.usermeta.Fullname, d.Student.username,
                                                                      file.Type,
                                                                      timezone.localtime(file.TimeStamp).strftime("%y%m%d%H%M%S"), name, ext
                                                                      ), fstream.read())
                except (IOError, ValueError):  # happens if a file is referenced from database but does not exist on disk.
                    return render(request, 'base.html', {
                        'Message': 'These files cannot be downloaded, please contact support staff. (Error on file: "{}")'.format(
                            file)})
    if empty:
        return render(request, 'base.html', {'Message': 'Your students did not upload any files yet.', 'return': 'students:liststudents', 'returnget': get_timeslot().pk})
    in_memory.seek(0)
    response = HttpResponse(content_type="application/zip")
    response['Content-Disposition'] = f'attachment; filename="studentfiles {timeslot}.zip"'
    response.write(in_memory.read())
    return response
