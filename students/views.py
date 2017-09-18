import json
import time

import channels
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Max
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render, redirect

from BepMarketplace.decorators import can_view_proposal, phase3_only, student_only
from professionalskills.models import StudentFile
from proposals.cacheprop import getProp
from proposals.models import Proposal
from general_view import get_timephase_number
from tracking.models import ApplicationTracking
from .forms import FileAddForm, FileEditForm
from .models import Application
from students.models import Distribution


@student_only()
def listApplications(request):
    """
    List the applications of a student, with a button to retract the application
    
    :param request:
    """
    return render(request, "students/ListApplications.html", context={
        "applications" : request.user.applications.all
    })


@login_required
@phase3_only
def prioUp(request, application_id):
    """
    Increase the priority of an application of a student.
    
    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
    if targetapp.Student != request.user:
        return render(request, "base.html", context={
            "Message" : "You are not the owner of this application!",
            "return": 'students:listapplications',
        })
    if targetapp.Priority == 1:
        return render(request, "base.html", context={
            "Message" : "Already at top priority",
            "return"  : 'students:listapplications',
        })
    swappapp = Application.objects.filter(Q(Student=request.user) & Q(Priority=targetapp.Priority - 1))[0]
    swappapp.Priority += 1
    targetapp.Priority -= 1
    swappapp.save()
    targetapp.save()

    return redirect('students:listapplications')


@login_required
@phase3_only
def prioDown(request, application_id):
    """
    Decrease the priority of an application of a student.
    
    :param request:
    :param application_id: Application id
    """
    targetapp = get_object_or_404(Application, pk=application_id)
    if targetapp.Student != request.user:
        return render(request, "base.html", context={
            "Message" : "You are not the owner of this application!",
            "return": 'students:listapplications',
        })
    if targetapp.Priority == settings.MAX_NUM_APPLICATIONS:
        return render(request, "base.html", context={
            "Message": "Already at bottom priority",
            "return": 'students:listapplications',
        })
    apps = Application.objects.filter(Q(Student=request.user) & Q(Priority=targetapp.Priority + 1))
    if len(apps) == 0:
        return render(request, "base.html", context={
            "Message": "Already at bottom priority",
            "return": 'students:listapplications',
        })
    swappapp = apps[0]
    swappapp.Priority -= 1
    targetapp.Priority += 1
    swappapp.save()
    targetapp.save()

    return redirect('students:listapplications')


@login_required
@phase3_only
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

    for app in request.user.applications.all():
        if app.Priority > appl.Priority:
            app.Priority -= 1
            app.save()
    appl.delete()
    return render(request, "base.html", context={
        "Message" : "Deleted application",
        "return": 'students:listapplications',
    })


@can_view_proposal
@phase3_only
@student_only()
def applyToProposal(request, pk):
    """
    Let a user apply to a proposal. Called after confirmapply.
    
    :param request:
    :param pk: id of a proposal.
    """
    prop = getProp(pk)
    if request.user.personal_proposal.exists():
        return render(request, "base.html", context={
            "Message": "You cannot apply because there is a private proposal for you.",
        })
    if request.user.applications.count() >= settings.MAX_NUM_APPLICATIONS:
        return render(request, "base.html", context={
                "Message" : "already at max ammount of applied proposals<br>"
                            "retract one first before continuing",
                "return": 'students:listapplications',
            })
    if Application.objects.filter(Q(Proposal=prop) & Q(Student=request.user)).exists():
        return render(request, "base.html", context={
            "Message" : "You already applied to this proposal.",
            "return"  : 'students:listapplications',
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
    highestprio = request.user.applications.aggregate(Max('Priority'))['Priority__max']
    appl.Student = request.user
    if highestprio is None:
        appl.Priority = 1
    else:
        appl.Priority = highestprio + 1
    appl.save()
    return render(request, "base.html", context={
        "Message" : "Application saved with priority number {}".format(appl.Priority),
        "return"  : 'students:listapplications',
    })


@can_view_proposal
@phase3_only
@student_only()
def confirmApplication(request, pk):
    """
    After a student presses apply on a proposal, he/she has to confirm the application on this page.
    This page also checks whether the user is allowed to apply
    
    :param request:
    :param pk: id of the proposal
    """
    if request.user.personal_proposal.exists():
        return render(request, "base.html", context={
            "Message": "You cannot apply because there is a private proposal for you.",
        })
    if request.user.groups.count() != 0:
        return render(request, "base.html", {"Message":"Only students can apply"})
    prop = getProp(pk)
    if prop.Status < 4 or prop.Private.count() > 0:
        raise PermissionDenied("Didn't think so, nice try")
    if Application.objects.filter(Q(Proposal=prop) & Q(Student=request.user)).exists():
        return render(request, "base.html", context={
            "Message" : "You already applied to this proposal.",
            "return"  : 'students:listapplications',
        })
    return render(request, "students/ApplyToProposal.html", context = {
        "proposal" : get_object_or_404(Proposal, pk=pk),
                                         })


@student_only()
def addFile(request):
    """
    For students to upload a file. Used for the hand in system.
    Responsibles, supervisors and trackheads can then view the files of their students.
    support staff can see all student files.
    
    :param request:
    """
    if get_timephase_number() < 6:
        raise PermissionDenied("Student files are not available in this phase")

    if request.user.groups.exists():
        raise PermissionDenied("Only for students")

    dist = get_object_or_404(Distribution, Student=request.user)

    if request.method == 'POST':
        form = FileAddForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            file = form.save(commit=False)
            file.Distribution = dist
            file.save()
            return render(request, "base.html",
                          {"Message": "File uploaded!", "return": "professionalskills:listownfiles"})
    else:
        form = FileAddForm(request=request)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Upload a file ', 'buttontext': 'Save'})


@student_only()
def editFiles(request):
    """
    For students to edit uploaded files. Used for the hand in system.
    Responsibles, supervisors and trackheads can then view the files of their students.
    support staff can see all student files.
    
    :param request:
    """
    if get_timephase_number() < 6:
        raise PermissionDenied("Student files are not available in this phase")

    if request.user.groups.exists():
        raise PermissionDenied("Only for students")

    dist = get_object_or_404(Distribution, Student=request.user)

    formSet = modelformset_factory(StudentFile, form=FileEditForm, can_delete=True, extra=0)
    qu = StudentFile.objects.filter(Distribution=dist)
    formset = formSet(queryset=qu)

    if request.method == 'POST':
        formset = formSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "File changes saved!", "return": "professionalskills:listownfiles"})
        return render(request, "base.html",
                      {"Message": "Error occurred during editing files. Possibly the file has wrong dimensions or wrong filetype.", "return": "students:editfiles"})
    else:
        return render(request, 'GenericForm.html', {'formset': formset, 'formtitle': 'All your uploaded files', 'buttontext': 'Save changes'})
