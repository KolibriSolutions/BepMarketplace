import json
import time

import channels
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect

from BepMarketplace.decorators import can_view_proposal, can_apply, student_only, can_access_professionalskills
from professionalskills.models import StudentFile
from proposals.cacheprop import getProp
from proposals.models import Proposal
from students.models import Distribution
from timeline.utils import get_timeslot
from tracking.models import ApplicationTracking
from .forms import StudentFileForm
from .models import Application


def get_all_applications(user):
    """
    Get a users applications for this timeslot

    :param request:
    :return:
    """
    return user.applications.filter(Proposal__TimeSlot=get_timeslot())


@student_only()
def listApplications(request):
    """
    List the applications of a student, with a button to retract the application
    
    :param request:
    """
    return render(request, 'students/ListApplications.html', context={
        'applications': get_all_applications(request.user)
    })


@can_apply
def prioUp(request, application_id):
    """
    Increase the priority of an application of a student.
    
    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
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
    swappapp = get_all_applications(request.user).filter(Q(Priority=targetapp.Priority - 1))[0]
    swappapp.Priority += 1
    targetapp.Priority -= 1
    swappapp.save()
    targetapp.save()
    return redirect('students:listapplications')


@can_apply
def prioDown(request, application_id):
    """
    Decrease the priority of an application of a student.
    
    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
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
    apps = get_all_applications(request.user).filter(Q(Priority=targetapp.Priority + 1))
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
def retractApplication(request, application_id):
    """
    Let a user un-apply / retract an application.
    
    :param request:
    :param application_id: Application id
    """
    appl = get_object_or_404(Application, pk=application_id)

    track = ApplicationTracking()
    track.Proposal = appl.Proposal
    track.Student = request.user
    track.Type = 'r'
    track.save()

    channels.Group('livestream').send({'text': json.dumps({
        'time': time.strftime('%H:%M:%S'),
        'event': 'retract',
        'proposal': appl.Proposal.id,
        'user': request.user.get_full_name(),
    })})

    for app in get_all_applications(request.user):
        if app.Priority > appl.Priority:
            app.Priority -= 1
            app.save()
    appl.delete()
    return render(request, 'base.html', context={
        'Message': 'Deleted application',
        'return': 'students:listapplications',
    })


@can_view_proposal
@can_apply
def applyToProposal(request, pk):
    """
    Let a user apply to a proposal. Called after confirmapply.
    
    :param request:
    :param pk: id of a proposal.
    """
    prop = getProp(pk)
    if prop.Status < 4:
        raise PermissionDenied('This proposal is not public, application is not possible.')

    if get_all_applications(request.user).count() >= settings.MAX_NUM_APPLICATIONS:
        return render(request, 'base.html', context={
                'Message': 'already at max ammount of applied proposals<br>'
                           'retract one first before continuing',
                'return': 'students:listapplications',
            })
    if get_all_applications(request.user).filter(Q(Proposal=prop)).exists():
        return render(request, 'base.html', context={
            'Message': 'You already applied to this proposal.',
            'return': 'students:listapplications',
        })

    track = ApplicationTracking()
    track.Proposal = prop
    track.Student = request.user
    track.Type = 'a'
    track.save()

    channels.Group('livestream').send({'text': json.dumps({
        'time': time.strftime('%H:%M:%S'),
        'event': 'apply',
        'proposal': prop.id,
        'user': request.user.get_full_name(),
    })})

    appl = Application()
    appl.Proposal = prop
    highestprio = get_all_applications(request.user).aggregate(Max('Priority'))['Priority__max']
    appl.Student = request.user
    if highestprio is None:
        appl.Priority = 1
    else:
        appl.Priority = highestprio + 1
    appl.save()
    return render(request, 'base.html', context={
        'Message': 'Application saved with priority number {}'.format(appl.Priority),
        'return'  : 'students:listapplications',
    })


@can_view_proposal
@can_apply
def confirmApplication(request, pk):
    """
    After a student presses apply on a proposal, he/she has to confirm the application on this page.
    This page also checks whether the user is allowed to apply
    
    :param request:
    :param pk: id of the proposal
    """
    prop = getProp(pk)
    if prop.Status < 4:
        raise PermissionDenied('This proposal is not public, application is not possible.')

    if get_all_applications(request.user).filter(Q(Proposal=prop)).exists():
        return render(request, 'base.html', context={
            'Message': 'You already applied to this proposal.',
            'return'  : 'students:listapplications',
        })
    return render(request, 'students/ApplyToProposal.html', context = {
        'proposal': get_object_or_404(Proposal, pk=pk),
                                         })


@student_only()
@can_access_professionalskills
def addFile(request):
    """
    For students to upload a file. Used for the hand in system.
    Responsibles, assistants and trackheads can then view the files of their students.
    support staff can see all student files.
    
    :param request:
    """
    dist = get_object_or_404(Distribution, Student=request.user)

    if request.method == 'POST':
        form = StudentFileForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            file = form.save(commit=False)
            file.Distribution = dist
            file.save()
            return render(request, 'base.html',
                          {'Message': 'File uploaded!', 'return': 'professionalskills:listownfiles'})
    else:
        form = StudentFileForm(request=request)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Upload a file ', 'buttontext': 'Save'})


@student_only()
@can_access_professionalskills
def editFile(request, pk):
    """
    For students to edit a uploaded file. Used for the hand in system.
    Responsibles, assistants and trackheads can then view the files of their students.
    support staff can see all student files.
    
    :param request:
    """
    file = get_object_or_404(StudentFile, id=pk)
    dist = request.user.distributions.filter(Timeslot=get_timeslot()).get()
    if request.method == 'POST':
        form = StudentFileForm(request.POST, request.FILES, request=request, instance=file)
        if form.is_valid():
            if form.has_changed():
                file = form.save(commit=False)
                file.Distribution = dist
                file.save()
                return render(request, 'base.html',
                          {'Message': 'File changed!', 'return': 'professionalskills:listownfiles'})
            else:
                return render(request, 'base.html',
                              {'Message': 'No change made.', 'return': 'professionalskills:listownfiles'})
    else:
        form = StudentFileForm(request=request, instance=file)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Edit a file ', 'buttontext': 'Save'})
