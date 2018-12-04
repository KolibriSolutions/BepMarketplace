import random
import zipfile
from datetime import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.timezone import localtime
from xhtml2pdf import pisa

from BepMarketplace.decorators import can_access_professionalskills, group_required, student_only, phase_required
from distributions.utils import get_distributions
from general_mail import send_mail, EmailThreadTemplate
from general_view import get_grouptype, get_all_students
from students.models import Distribution
from timeline.utils import get_timeslot
from .forms import FileTypeModelForm, ConfirmForm, StaffReponseForm, StudentGroupForm, StudentGroupChoice
from .models import FileType, StaffReponse, StudentFile, StudentGroup


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
def download_all_of_type(request, pk):
    """
    Download all files for a given filetype

    :param request:
    :param pk: id of the filetype
    :return:
    """
    ftype = get_object_or_404(FileType, pk=pk)

    in_memory = BytesIO()
    with zipfile.ZipFile(in_memory, 'w') as archive:
        for file in ftype.files.all():
            trck = file.Distribution.Proposal.Track
            with open(file.File.path, 'rb') as fstream:
                archive.writestr(
                    '{}/{}.{}'.format(str(trck), file.Distribution.Student.usermeta.get_nice_name().replace(' ', ''),
                                      file.File.name.split('.')[-1]), fstream.read())
    in_memory.seek(0)

    response = HttpResponse(content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(str(ftype.Name))

    response.write(in_memory.read())

    return response


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
                'Message': 'File Type created!',
                'return': 'professionalskills:filetypelist',
            })
    else:
        form = FileTypeModelForm()

    return render(request, 'GenericForm.html', {
        'formtitle': 'Create New FileType',
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
                    'Message': 'File Type saved!',
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
        'formtitle': 'Edit FileType',
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
            obj.delete()
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
def list_filetypes(request):
    """
    For students to view a list of all profskills they have to hand in.
    For type3/type6 staff also shows edit and download buttons

    :param request:
    :return:
    """
    return render(request, 'professionalskills/listFileTypes.html', {
        'filetypes': FileType.objects.filter(TimeSlot=get_timeslot())
    })


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
def list_files_of_type(request, pk):
    """
    Lists all files of one type of professional skill.

    :param request:
    :param pk: filetype to show delivered files for
    :return:
    """
    ftype = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/listFilesOfType.html', {
        'type': ftype,
        'files': StudentFile.objects.filter(Type=ftype).distinct()
    })


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
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
    missing_students.sort(key=lambda d: str(d.Student.last_name))
    return render(request, 'professionalskills/listFailStudents.html', {
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
    dist = get_object_or_404(Distribution, pk=pk)
    respondrights = False
    editrights = False
    if dist.Student == request.user:
        editrights = True
    elif request.user in dist.Proposal.Assistants.all() \
            or request.user == dist.Proposal.ResponsibleStaff \
            or request.user == dist.Proposal.Track.Head:
        respondrights = True
    elif get_grouptype("3") in request.user.groups.all() or get_grouptype('6') in request.user.groups.all():
        pass
    else:
        raise PermissionDenied("You are not allowed to view these files")

    files = dist.files.all()
    return render(request, "professionalskills/listFiles.html",
                  {"dist": dist, "files": files, "respond": respondrights, 'edit': editrights})


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
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


@group_required('type1staff', 'type2staff')
@can_access_professionalskills
@phase_required(6, 7)
def respond_file(request, pk):
    """
    Form to let a staff member give a response to a students file.

    :param request:
    :param pk:
    :return:
    """

    fileobj = get_object_or_404(StudentFile, pk=pk)
    if (request.user not in fileobj.Distribution.Proposal.Assistants.all() and
        request.user != fileobj.Distribution.Proposal.ResponsibleStaff) \
            or not fileobj.Type.CheckedBySupervisor:
        raise PermissionDenied("You cant respond to this file")

    try:
        responseobj = fileobj.staffreponse
        responseobj.Staff = request.user
        statusorig = responseobj.Status
    except:
        responseobj = StaffReponse()
        responseobj.File = fileobj
        responseobj.Staff = request.user
        statusorig = None

    if request.method == 'POST':
        form = StaffReponseForm(request.POST, instance=responseobj)
        if form.is_valid():
            if form.cleaned_data['Status'] != statusorig:
                send_mail('Professional skill feedback', 'email/prvresponse.html', {
                    'student': fileobj.Distribution.Student,
                    'status': form.cleaned_data['Status'],
                    'explanation': form.cleaned_data['Explanation'],
                    'type': fileobj.Type.Name,
                }, fileobj.Distribution.Student.email)
            form.save()
            return render(request, 'base.html', {
                'Message': 'Response saved!',
                'return': 'support:liststudents',
            })
    else:
        form = StaffReponseForm(instance=responseobj)

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Respond to {} from {}'.format(fileobj.Type.Name, fileobj.Distribution.Student.usermeta.get_nice_name())
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
    dist = get_object_or_404(Distribution, Student=request.user)
    return list_student_files(request, dist.pk)


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
def print_forms(request):
    """
    Export PDF of all distributed students

    :param request:
    :return:
    """
    template = get_template('professionalskills/printPrvResults.html')
    pages = []
    for dstr in Distribution.objects.all():
        obj = {
            'student': dstr.Student,
            'proposal': dstr.Proposal,
            'files': StaffReponse.objects.filter(File__Distribution=dstr).order_by('File__Type__id'),
        }
        try:
            obj['room'] = dstr.presentationtimeslot.Presentations.AssessmentRoom
            obj['time'] = dstr.presentationtimeslot.DateTime
        except:
            pass
        pages.append(obj)

    # return render(request, 'professionalskills/printPrvResults.html', {
    #     'pages' : pages,
    # })

    htmlblock = template.render({
        'pages': pages
    })

    buffer = BytesIO()
    pisaStatus = pisa.CreatePDF(htmlblock.encode('utf-8'), dest=buffer, encoding='utf-8')
    if pisaStatus.err:
        raise Exception("Pisa Failed PDF creation in print PRV results")
    buffer.seek(0)
    response = HttpResponse(buffer, 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Professional-Skills-export.pdf"'
    return response


@group_required('type3staff', 'type6staff')
def create_group(request, pk=None):
    """
    Create a group of students for PRV's. This does not yet fill the group with students.

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
        'formtitle': 'Create new Group',
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


@group_required('type3staff', 'type6staff')
def list_groups(request, pk):
    """
    List all groups of students for one PRV.

    :param request:
    :param pk:
    :return:
    """
    filetype = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/listAllGroups.html', {
        'groups': filetype.groups.all(),
        'PRV': filetype
    })


@login_required
@phase_required(6, 7)
def list_group_members(request, pk):
    """
    List all students in a prv group

    :param request:
    :param pk:
    :return:
    """
    group = get_object_or_404(StudentGroup, pk=pk)
    return render(request, 'GenericList.html', {
        'items': [mem.usermeta.get_nice_name() for mem in group.Members.all()],
        'header': format_html('<h1>Members of group {}</h1><h2>{}</h2><h3>Starts {}</h3><br/>Capacity: {}/{}'
                              .format(group.Number, group.PRV, localtime(group.Start).strftime("%a %d %b at %H:%M"),
                                      group.Members.count(), group.Max)),
    })


@group_required('type3staff', 'type6staff')
@phase_required(6, 7)
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
def switch_group(request, frompk, topk):
    """
    Lets a student switch between prv groups. This function is usually not called via URL, only direct.

    :param request:
    :param frompk: original student group
    :param topk: group to switch to
    :return:
    """
    fromgroup = get_object_or_404(StudentGroup, pk=frompk)
    togroup = get_object_or_404(StudentGroup, pk=topk)

    if fromgroup.PRV != togroup.PRV:
        raise PermissionDenied("Groups must be for the same professional skill.")
    if fromgroup not in request.user.studentgroups.all():
        raise PermissionDenied('User is not in from group')

    fromgroup.Members.remove(request.user)
    togroup.Members.add(request.user)
    togroup.save()
    fromgroup.save()

    return render(request, 'base.html', {
        'Message': 'Switched to group {}'.format(togroup),
        'return': 'professionalskills:listowngroups',
    })


@student_only()
@can_access_professionalskills
def list_own_groups(request):
    """
    List all prv groups where a student is in. With a form for each group to switch to another group.

    :param request:
    :return:
    """
    if request.method == 'POST':
        for g in request.user.studentgroups.all():
            f = StudentGroupChoice(request.POST, initial={'Group': g}, prefix=str(g.PRV.pk), PRV=g.PRV)
            if f.is_valid():
                try:
                    switch_group(request, g.pk, f.cleaned_data['Group'].pk)
                except ValidationError:
                    return render(request, 'base.html', {
                        'Switched group is full!'
                    })
        return render(request, 'base.html', {
            'Message': 'Switched groups',
            'return': 'professionalskills:listowngroups',
        })

    groups = []
    for g in request.user.studentgroups.all():
        f = StudentGroupChoice(initial={'Group': g}, prefix=str(g.PRV.pk), PRV=g.PRV)
        groups.append((g, f))
    return render(request, 'professionalskills/listAllOwnGroups.html', {
        'groups': groups
    })
