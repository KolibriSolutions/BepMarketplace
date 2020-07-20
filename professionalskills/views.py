#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import random
import zipfile
from datetime import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.timezone import localtime
from xhtml2pdf import pisa

from distributions.utils import get_distributions
from general_form import ConfirmForm
from general_mail import send_mail, EmailThreadTemplate
from general_model import delete_object
from general_view import get_grouptype, get_all_students
from index.decorators import group_required, student_only
from presentations.utils import planning_public
from professionalskills.decorators import can_access_professionalskills
from students.models import Distribution
from timeline.decorators import phase_required
from timeline.utils import get_timeslot, get_timephase_number
from .forms import FileTypeModelForm, StaffResponseForm, StudentGroupForm, StudentGroupChoice, FileExtensionForm, StaffResponseFileAspectResultForm, StaffResponseFileAspectForm
from .models import FileType, StaffResponse, StudentFile, StudentGroup, FileExtension, StaffResponseFileAspectResult, StaffResponseFileAspect


@group_required('type3staff', 'type6staff')
def download_all_of_type(request, pk):
    """
    Download all files for a given filetype

    :param request:
    :param pk: id of the filetype
    :return:
    """
    ftype = get_object_or_404(FileType, pk=pk)
    if ftype.TimeSlot == get_timeslot():  # current year download
        if get_timephase_number() < 5:  # only in phase 5, 6 and 7
            raise PermissionDenied("This page is not available in the current time phase.")
    in_memory = BytesIO()
    with zipfile.ZipFile(in_memory, 'w') as archive:
        for file in ftype.files.all():
            trck = file.Distribution.Proposal.Track
            fname = file.Distribution.Student.usermeta.get_nice_name().split()[-1] + "".join(
                file.Distribution.Student.usermeta.get_nice_name().split(' ')[:-1])
            try:
                with open(file.File.path, 'rb') as fstream:
                    archive.writestr(
                        '{}/{}.{}'.format(str(trck), fname,
                                          file.File.name.split('.')[-1]), fstream.read())
            except (IOError, ValueError):  # happens if a file is referenced from database but does not exist on disk.
                return render(request, 'base.html', {'Message': 'These files cannot be downloaded, please contact support staff. (Error on file: "{}")'.format(file)})
    in_memory.seek(0)

    response = HttpResponse(content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(str(ftype.Name))

    response.write(in_memory.read())

    return response


@can_access_professionalskills
def list_filetypes(request):
    """
    For students to view a list of all profskills they have to hand in.
    For type3/type6 staff also shows edit and download buttons

    :param request:
    :return:
    """
    return render(request, 'professionalskills/list_professional_skills.html', {
        'filetypes': FileType.objects.filter(TimeSlot=get_timeslot())
    })


@group_required('type3staff', 'type6staff')
def create_filetype(request):
    """
    Create a file type that can be used for any professional skill hand-in document.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = FileTypeModelForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                'Message': 'File type created!',
                'return': 'professionalskills:filetypelist',
            })
    else:
        form = FileTypeModelForm()

    return render(request, 'GenericForm.html', {
        'formtitle': 'Create new file type',
        'form': form,
        'buttontext': 'Create'
    })


@group_required('type3staff', 'type6staff')
def edit_filetype(request, pk):
    """
    Edit a file type.

    :param request:
    :param pk: id of the file type.
    :return:
    """
    obj = get_object_or_404(FileType, pk=pk)
    if request.method == 'POST':
        form = FileTypeModelForm(request.POST, instance=obj)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return render(request, 'base.html', {
                    'Message': 'File type saved!',
                    'return': 'professionalskills:filetypelist'
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'No changes made.',
                    'return': 'professionalskills:filetypelist',
                })
    else:
        form = FileTypeModelForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'formtitle': 'Edit file type',
        'form': form,
        'buttontext': 'Save'
    })


@group_required('type3staff', 'type6staff')
def delete_filetype(request, pk):
    """
    Delete a file type.

    :param request:
    :param pk: id of the file type
    :return:
    """
    obj = get_object_or_404(FileType, pk=pk)

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            delete_object(obj)
            return render(request, 'base.html', {
                'Message': 'File type deleted.',
                'return': 'professionalskills:filetypelist',
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm deletion of File type {}'.format(obj),
        'buttontext': 'Confirm'
    })


@can_access_professionalskills
def list_filetype_aspects(request, pk):
    """
    List all grading aspects for a prv file.

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(FileType, pk=pk)
    if not obj.CheckedBySupervisor:
        raise PermissionDenied('This file type does not need a response from the supervisor.')
    aspects = obj.aspects.all()
    return render(request, 'professionalskills/list_aspects.html', {
        'file': obj,
        'aspects': aspects,
        'aspectoptions': StaffResponseFileAspectResult.ResultOptions
    })


@group_required('type3staff', 'type6staff')
def add_filetype_aspect(request, pk):
    """
    Add prv result aspect

    :param request:
    :param pk: pk of FileType to add aspect to
    :return:
    """
    file = get_object_or_404(FileType, pk=pk)
    if request.method == 'POST':
        form = StaffResponseFileAspectForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.File = file
            obj.save()
            return render(request, 'base.html', {
                'Message': '{} created!'.format(obj),
                'return': 'professionalskills:filetypeaspects',
                'returnget': file.pk,
            })
    else:
        form = StaffResponseFileAspectForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Create aspect for {}'.format(file),
        'buttontext': 'Create'
    })


@group_required('type3staff', 'type6staff')
def edit_filetype_aspect(request, pk):
    """
    Edit a file type aspect.

    :param request:
    :param pk: id of the file type aspect.
    :return:
    """
    obj = get_object_or_404(StaffResponseFileAspect, pk=pk)
    if request.method == 'POST':
        form = StaffResponseFileAspectForm(request.POST, instance=obj)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return render(request, 'base.html', {
                    'Message': 'File type aspect saved!',
                    'return': 'professionalskills:filetypeaspects',
                    'returnget': obj.File.pk,
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'No changes made.',
                    'return': 'professionalskills:filetypeaspects',
                    'returnget': obj.File.pk,
                })
    else:
        form = StaffResponseFileAspectForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'formtitle': 'Edit file type aspect',
        'form': form,
        'buttontext': 'Save'
    })


@group_required('type3staff', 'type6staff')
def delete_filetype_aspect(request, pk):
    """
    Delete a file type grade aspect.

    :param request:
    :param pk: id of the file type aspect
    :return:
    """
    obj = get_object_or_404(StaffResponseFileAspect, pk=pk)
    pk = obj.File.pk  # store original linked File
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            delete_object(obj)
            return render(request, 'base.html', {
                'Message': 'File type aspect deleted.',
                'return': 'professionalskills:filetypeaspects',
                'returnget': pk,
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm deletion of file type aspect {}'.format(obj),
        'buttontext': 'Confirm'
    })


@group_required('type3staff', 'type6staff')
@phase_required(5, 6, 7)
def list_files_of_type(request, pk):
    """
    Lists all files of one type of professional skill.

    :param request:
    :param pk: filetype to show delivered files for
    :return:
    """
    ftype = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/list_files.html', {
        'type': ftype,
        'files': StudentFile.objects.filter(Type=ftype).distinct()
    })


@group_required('type3staff', 'type6staff')
@phase_required(5, 6, 7)
def list_missing_of_type(request, pk):
    """
    Lists all students that did not hand in a file with specified type.

    :param request:
    :param pk: filetype to show missing students for
    :return:
    """
    ftype = get_object_or_404(FileType, pk=pk)
    missing_students = []
    for dist in get_distributions(request.user):
        if dist.files.filter(Type=ftype).count() == 0:
            missing_students.append(dist)
    return render(request, 'professionalskills/list_missing_students.html', {
        'type': ftype,
        'distributions': missing_students,
    })


@can_access_professionalskills
def list_student_files(request, pk):
    """
    List files of a specified student.
    Used for the student self, for his supervisor, responsible, trackhead and for support staff.

    :param request:
    :param pk: id of distribution
    :return:
    """
    if get_grouptype('2u') in request.user.groups.all():
        raise PermissionDenied("Please have your account verified first.")

    dist = get_object_or_404(Distribution, pk=pk)

    # check permissions
    if get_grouptype('3') in request.user.groups.all() or \
            get_grouptype('6') in request.user.groups.all() or \
            request.user in dist.Proposal.Assistants.all() or \
            request.user == dist.Proposal.ResponsibleStaff or \
            request.user == dist.Proposal.Track.Head or \
            request.user == dist.Student:
        # allowed
        pass
    elif planning_public():
        try:
            if request.user in dist.presentationtimeslot.Presentations.Assessors.all():
                # assessor can view files
                pass
            else:
                # user is not assessor or planning is not public
                raise PermissionDenied("You are not allowed to view these files")
        except:
            # presentations not yet planned or presentationoptions do not exist.
            raise PermissionDenied("You are not allowed to view these files")
    else:
        raise PermissionDenied("You cannot view this file list.")

    # check edit rights
    if dist.TimeSlot == get_timeslot():
        # current timeslot
        respondrights = False
        editrights = False
        if dist.Student == request.user:
            editrights = True
        elif request.user in dist.Proposal.Assistants.all() \
                or request.user == dist.Proposal.ResponsibleStaff \
                or request.user == dist.Proposal.Track.Head \
                or get_grouptype('3') in request.user.groups.all():
            respondrights = True
    else:
        # no changing of history.
        respondrights = False
        editrights = False
    files = dist.files.all()
    return render(request, "professionalskills/list_files.html",
                  {"dist": dist, "files": files, "respond": respondrights, 'edit': editrights})


@group_required('type3staff', 'type6staff')
@phase_required(5, 6, 7)
def mail_overdue_students(request):
    """
    Mail students that didn't handin file before the deadline

    :param request:
    :return:
    """
    if request.method == "POST":
        form = ConfirmForm(request.POST)
        if form.is_valid():
            mails = []
            for dist in get_distributions(request.user):
                missingtypes = []
                for ftype in FileType.objects.all():
                    if ftype.Deadline >= datetime.today().date():
                        continue  # only mail if the deadline has passed.
                    if dist.files.filter(Type=ftype).count() == 0:
                        missingtypes.append(ftype)
                if len(missingtypes) > 0:
                    mails.append({
                        'template': 'email/overdueprvstudent.html',
                        'email': dist.Student.email,
                        'subject': 'Overdue professional skill delivery',
                        'context': {
                            'student': dist.Student,
                            'project': dist.Proposal,
                            'types': missingtypes,
                        }
                    })

            EmailThreadTemplate(mails).start()

            return render(request, "support/email_progress.html")
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        "form": form,
        "formtitle": "Confirm mailing overdue students",
        "buttontext": "Confirm"
    })


@can_access_professionalskills
@phase_required(5, 6, 7)
def view_response(request, pk):
    """
    Form to let a student view a staff response / rubric

    :param request:
    :param pk: pk of studentfile
    :return:
    """
    if get_grouptype('2u') in request.user.groups.all():
        raise PermissionDenied("Please have your account verified first.")

    fileobj = get_object_or_404(StudentFile, pk=pk)
    dist = fileobj.Distribution

    # check permissions
    if get_grouptype('3') in request.user.groups.all() or \
            get_grouptype('6') in request.user.groups.all() or \
            request.user in dist.Proposal.Assistants.all() or \
            request.user == dist.Proposal.ResponsibleStaff or \
            request.user == dist.Proposal.Track.Head or \
            request.user == dist.Student:
        # allowed
        pass
    elif planning_public():
        try:
            if request.user in dist.presentationtimeslot.Presentations.Assessors.all():
                # assessor can view files
                pass
            else:
                # user is not assessor or planning is not public
                raise PermissionDenied("You are not allowed to view these files")
        except:
            # presentations not yet planned or presentationoptions do not exist.
            raise PermissionDenied("You are not allowed to view these files")
    else:
        raise PermissionDenied("You cannot view this file list.")

    # get results
    try:
        responseobj = fileobj.staffresponse
    except StaffResponse.DoesNotExist:
        return render(request, 'base.html', {"Message": "This file is not (yet) graded."})

    aspect_forms = []
    for i, aspect in enumerate(fileobj.Type.aspects.all()):
        try:
            aspect_result = StaffResponseFileAspectResult.objects.get(Aspect=aspect, Response=responseobj)
        except StaffResponseFileAspectResult.DoesNotExist:
            aspect_result = StaffResponseFileAspectResult(Aspect=aspect, Response=responseobj)
        aspect_forms.append({
            "form": StaffResponseFileAspectResultForm(instance=aspect_result, prefix="aspect" + str(i)),
            "aspect": aspect
        })
    return render(request, 'professionalskills/view_response.html', {
        'file': fileobj,
        'response': responseobj,
        'aspectoptions': StaffResponseFileAspectResult.ResultOptions
    })


@group_required('type1staff', 'type2staff', 'type3staff')
@can_access_professionalskills
@phase_required(5, 6, 7)
def respond_file(request, pk):
    """
    Form to let a staff member give a response to a students file.

    :param request:
    :param pk:
    :return:
    """

    fileobj = get_object_or_404(StudentFile, pk=pk)
    if not get_grouptype('3') in request.user.groups.all():
        if (request.user not in fileobj.Distribution.Proposal.Assistants.all() and
            request.user != fileobj.Distribution.Proposal.ResponsibleStaff and
            request.user != fileobj.Distribution.Proposal.Track.Head) \
                or not fileobj.Type.CheckedBySupervisor:
            raise PermissionDenied("You cannot respond to this file.")
    if fileobj.Distribution.TimeSlot != get_timeslot():
        raise PermissionDenied("Changing history is not allowed.")

    try:
        responseobj = fileobj.staffresponse
        responseobj.Staff = request.user
        statusorig = responseobj.Status
    except StaffResponse.DoesNotExist:
        responseobj = StaffResponse()
        responseobj.File = fileobj
        responseobj.Staff = request.user
        statusorig = None

    if request.method == 'POST':
        aspect_forms = []
        for i, aspect in enumerate(fileobj.Type.aspects.all()):
            try:
                aspect_result = StaffResponseFileAspectResult.objects.get(Aspect=aspect, Response=responseobj)
            except StaffResponseFileAspectResult.DoesNotExist:
                aspect_result = StaffResponseFileAspectResult(Aspect=aspect, Response=responseobj)
            aspect_forms.append({
                "form": StaffResponseFileAspectResultForm(request.POST, instance=aspect_result, prefix="aspect" + str(i)),
                "aspect": aspect
            })
        response_form = StaffResponseForm(request.POST, instance=responseobj, prefix='response')
        if response_form.is_valid() and all([form['form'].is_valid() for form in aspect_forms]):
            if response_form.cleaned_data['Status'] != statusorig:
                send_mail('Professional skill feedback', 'email/prvresponse.html', {
                    'student': fileobj.Distribution.Student,
                    'status': response_form.cleaned_data['Status'],
                    'explanation': response_form.cleaned_data['Explanation'],
                    'type': fileobj.Type.Name,
                }, fileobj.Distribution.Student.email)
            response_form.save()
            # for first time saving, refetch all aspects as they are now tied to responseobj that is actually saved
            aspect_forms = []
            for i, aspect in enumerate(fileobj.Type.aspects.all()):
                try:
                    aspect_result = StaffResponseFileAspectResult.objects.get(Aspect=aspect, Response=responseobj)
                except StaffResponseFileAspectResult.DoesNotExist:
                    aspect_result = StaffResponseFileAspectResult(Aspect=aspect, Response=responseobj)
                aspect_forms.append({
                    "form": StaffResponseFileAspectResultForm(request.POST, instance=aspect_result, prefix="aspect" + str(i)),
                    "aspect": aspect
                })
            all([form['form'].save() for form in aspect_forms])
            return render(request, 'base.html', {
                'Message': 'Response saved!',
                'return': 'support:liststudents',
                'returnget': fileobj.Distribution.TimeSlot.pk,
            })
    else:
        aspect_forms = []
        for i, aspect in enumerate(fileobj.Type.aspects.all()):
            try:
                aspect_result = StaffResponseFileAspectResult.objects.get(Aspect=aspect, Response=responseobj)
            except StaffResponseFileAspectResult.DoesNotExist:
                aspect_result = StaffResponseFileAspectResult(Aspect=aspect, Response=responseobj)
            aspect_forms.append({
                "form": StaffResponseFileAspectResultForm(instance=aspect_result, prefix="aspect" + str(i)),
                "aspect": aspect
            })
        response_form = StaffResponseForm(instance=responseobj, prefix='response')

    return render(request, 'professionalskills/staffresponseform.html', {
        'form': response_form,
        'formtitle': 'Respond to {} from {}'.format(fileobj.Type.Name, fileobj.Distribution.Student.usermeta.get_nice_name()),
        'aspectforms': aspect_forms,
        "aspectlabels": StaffResponseFileAspectResult.ResultOptions,
    })


@student_only()
@can_access_professionalskills
def list_own_files(request):
    """
    Shows the list of files of a student. Files are attached to distributions-objects.
    This function calls the general file list function listStudentFiles with this student as argument.

    :param request:
    :return:
    """
    dist = get_object_or_404(Distribution, Student=request.user, TimeSlot=get_timeslot())
    return list_student_files(request, dist.pk)


@group_required('type3staff', 'type6staff')
@phase_required(5, 6, 7)
def print_forms(request):
    """
    Export PDF of all distributed students

    :param request:
    :return:
    """
    template = get_template('professionalskills/print_results.html')
    pages = []
    for dstr in Distribution.objects.filter(TimeSlot=get_timeslot()):
        obj = {
            'student': dstr.Student,
            'proposal': dstr.Proposal,
            'files': StaffResponse.objects.filter(File__Distribution=dstr).order_by('File__Type__id'),
        }
        try:
            obj['room'] = dstr.presentationtimeslot.Presentations.AssessmentRoom
            obj['time'] = dstr.presentationtimeslot.DateTime
        except:
            pass
        pages.append(obj)
    htmlblock = template.render({
        'pages': pages
    })

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(htmlblock.encode('utf-8'), dest=buffer, encoding='utf-8')
    if pisa_status.err:
        raise Exception("Pisa Failed PDF creation in print PRV results")
    buffer.seek(0)
    response = HttpResponse(buffer, 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Professional-Skills-export.pdf"'
    return response


@group_required('type3staff', 'type6staff')
def list_groups(request, pk):
    """
    List all groups of students for one PRV.

    :param request:
    :param pk:
    :return:
    """
    filetype = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/list_student_groups.html', {
        'groups': filetype.groups.all(),
        'PRV': filetype
    })


@group_required('type3staff', 'type6staff')
def create_group(request, pk=None):
    """
    Create a group of students for professional skills. This does not yet fill the group with students.

    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        form = StudentGroupForm(request.POST)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message': '{} created!'.format(obj),
            })
    else:
        if pk is not None:
            obj = StudentGroup(PRV=get_object_or_404(FileType, pk=pk))
            form = StudentGroupForm(instance=obj)
        else:
            form = StudentGroupForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Create new student group',
        'buttontext': 'Create'
    })


@group_required('type3staff', 'type6staff')
def edit_group(request, pk):
    """
    Edit a prv group.

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(StudentGroup, pk=pk)
    if request.method == 'POST':
        form = StudentGroupForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message': '{} saved!'.format(obj),
            })
    else:
        form = StudentGroupForm(instance=obj)
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit Group',
        'buttontext': 'Save'
    })


@login_required
@phase_required(5, 6, 7)
def list_group_members(request, pk):
    """
    List all students in a prv group

    :param request:
    :param pk:
    :return:
    """
    group = get_object_or_404(StudentGroup, pk=pk)
    if group.PRV.TimeSlot != get_timeslot():
        raise PermissionDenied("Only allowed for current timeslot.")
    return render(request, 'GenericList.html', {
        'items': [mem.usermeta.get_nice_name() for mem in group.Members.all()],
        'header': format_html('<h1>Members of group {}</h1><h2>{}</h2><h3>Starts {}</h3><br/>Capacity: {}/{}'
                              .format(group.Number, group.PRV, localtime(group.Start).strftime("%a %d %b at %H:%M"),
                                      group.Members.count(), group.Max)),
    })


@group_required('type3staff', 'type6staff')
@phase_required(5, 6, 7)
def assign(request, pk):
    """
    Assign all distributed students to one of the prv groups.

    :param request:
    :param pk:
    :return:
    """
    filetype = get_object_or_404(FileType, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            if filetype.groups.all().aggregate(Sum('Max'))['Max__sum'] < get_all_students().count():
                return render(request, 'base.html', {
                    'Message': 'Groups capacity not sufficient'
                })
            for group in filetype.groups.all():
                group.Members.clear()
                group.save()
            students = list(get_all_students())
            totalstudents = len(students)
            random.shuffle(students)
            groups = list(filetype.groups.all())
            totaldistributed = 0
            while totaldistributed < totalstudents:
                for g in [g for g in groups if g.Members.count() < g.Max]:
                    try:
                        g.Members.add(students.pop(0))
                        totaldistributed += 1
                    except IndexError:
                        break
            for g in groups:
                g.save()

            return render(request, 'base.html', {
                'Message': 'Students divided over the groups'
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm reshuffling students for {}'.format(filetype),
        'buttontext': 'Confirm'
    })


@student_only()
@can_access_professionalskills
def switch_group(request, pk):
    """
    Lets a student switch between prv groups. This function is usually not called via URL, only direct.

    :param request:
    :param pk: pk of PRV for which groups are switched.
    :return:
    """
    prv = get_object_or_404(FileType, pk=pk)
    try:
        stdgrp = prv.groups.get(Members=request.user)
    except StudentGroup.DoesNotExist:
        raise PermissionDenied("You are not enrolled in a group for this skill.")
    from_group = request.user.studentgroups.get(PRV=prv)
    if request.method == 'POST':
        form = StudentGroupChoice(request.POST, PRV=prv)
        if form.is_valid():
            to_group = form.cleaned_data.get('Group')
            if from_group.PRV != to_group.PRV:
                raise PermissionDenied("Groups must be for the same professional skill.")
            if from_group not in request.user.studentgroups.all():
                raise PermissionDenied('User is not in from group')
            from_group.Members.remove(request.user)
            to_group.Members.add(request.user)
            to_group.save()
            from_group.save()
            return render(request, 'base.html', {
                'Message': 'Switched to group {}'.format(to_group),
                'return': 'professionalskills:listowngroups',
            })
    else:
        form = StudentGroupChoice(initial={'Group': stdgrp}, PRV=prv)

    return render(request, 'GenericForm.html', {
        'form': form,
        'title': 'Change group for {}'.format(prv)
    })


@student_only()
@can_access_professionalskills
def list_own_groups(request):
    """
    List all prv groups where a student is in. With a form for each group to switch to another group.

    :param request:
    :return:
    """
    return render(request, 'professionalskills/list_groups.html', {
        'groups': StudentGroup.objects.filter(PRV__TimeSlot=get_timeslot(), Members=request.user).distinct()
    })


@group_required('type3staff', 'type6staff')
def edit_extensions(request):
    """
    Edit known file extensions

    :param request:
    :return:
    """
    form_set = modelformset_factory(FileExtension, form=FileExtensionForm, can_delete=True, extra=3)
    qu = FileExtension.objects.all()
    formset = form_set(queryset=qu)

    if request.method == 'POST':
        formset = form_set(request.POST)
        if formset.is_valid():
            formset.save()  # manytomany field, so will always be set_null on delete of extension.
            return render(request, "base.html", {"Message": "File extensions saved!", "return": "index:index"})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': 'All student file extensions', 'buttontext': 'Save'})
