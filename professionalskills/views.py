import zipfile
from datetime import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa

from BepMarketplace.decorators import group_required, student_only
from students.models import Distribution
from general_mail import send_mail, EmailThreadMultipleTemplate
from distributions.utils import get_distributions
from timeline.utils import get_timeslot, get_timephase_number
from timeline.models import TimeSlot
from .forms import FileTypeModelForm, ConfirmForm, StaffReponseForm, StudentGroupForm, StudentGroupChoice
from .models import FileType, StaffReponse, StudentFile, StudentGroup
from general_view import get_grouptype, get_all_students
from BepMarketplace.decorators import can_access_professionalskills
import random
from django.db.models import Sum
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError

@group_required('type3staff', 'type6staff')
def downloadAll(request, pk):
    """
    Download all files for a given filetype

    :param request:
    :param pk: id of the filetype
    :return:
    """
    if get_timephase_number() < 5:
        raise PermissionDenied('Students are not yet distributed to projects.')

    ftype = get_object_or_404(FileType, pk=pk)

    in_memory = BytesIO()
    with zipfile.ZipFile(in_memory, 'w') as archive:
        for file in ftype.files.all():
            trck = file.Distribution.Proposal.Track
            with open(file.File.path, 'rb') as fstream:
                archive.writestr('{}/{}.{}'.format(str(trck), file.Distribution.Student.get_full_name().replace(' ', ''),
                                                   file.File.name.split('.')[-1]), fstream.read())
    in_memory.seek(0)

    response = HttpResponse(content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="{}.zip"'.format(str(ftype.Name))

    response.write(in_memory.read())

    return response


@group_required('type3staff', 'type6staff')
def createFileType(request):
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
                'Message' : 'File Type created!',
                'return'  : 'professionalskills:filetypelist',
            })
    else:
        form = FileTypeModelForm()

    return render(request, 'GenericForm.html', {
        'formtitle' : 'Create New FileType',
        'form'      : form,
        'buttontext': 'Create'
    })


@group_required('type3staff', 'type6staff')
def editFileType(request, pk):
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
                    'Message' : 'File Type saved!',
                    'return'  : 'professionalskills:filetypelist'
                })
            else:
                return render(request, 'base.html', {
                    'Message' : 'No changes made.',
                    'return'  : 'professionalskills:filetypelist',
                })
    else:
        form = FileTypeModelForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'formtitle' : 'Edit FileType',
        'form'      : form,
        'buttontext': 'Save'
    })


@group_required('type3staff', 'type6staff')
def deleteFileType(request, pk):
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
                'Message' : 'File type deleted.',
                'return' : 'professionalskills:filetypelist',
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm deletion of File type {}'.format(obj),
        'buttontext' : 'Confirm'
    })


@login_required
@can_access_professionalskills
def listFileType(request):
    """
    For students to view a list of all profskills they have to hand in.
    For type3/type6 staff also shows edit and download buttons

    :param request:
    :return:
    """
    return render(request, 'professionalskills/listFileTypes.html', {
        'filetypes' : FileType.objects.filter(TimeSlot=get_timeslot())
    })


@group_required('type3staff', 'type6staff')
def listFilePerType(request, pk):
    """
    Lists all files of one type of professional skill.

    :param request:
    :param pk: filetype to show delivered files for
    :return:
    """
    if get_timephase_number() < 5:
        raise PermissionDenied('Students are not yet distributed to projects.')

    ftype = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/listFilesOfType.html', {
        'type' : ftype,
        'files' : StudentFile.objects.filter(Type=ftype).distinct()
    })


@group_required('type3staff', 'type6staff')
def listMissingPerType(request, pk):
    """
    Lists all students that did not hand in a file with specified type.

    :param request:
    :param pk: filetype to show missing students for
    :return:
    """

    if get_timephase_number() < 5:
        raise PermissionDenied("Student files are not available in this phase")

    ftype = get_object_or_404(FileType, pk=pk)
    failStudents = []
    for dist in get_distributions(request.user):
        if dist.files.filter(Type=ftype).count() == 0:
            failStudents.append(dist)
    failStudents.sort(key=lambda d: str(d.Student.last_name))
    return render(request, 'professionalskills/listFailStudents.html', {
        'type' : ftype,
        'distributions' : failStudents,
    })


@login_required
@can_access_professionalskills
def listStudentFiles(request, pk):
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
        or request.user == dist.Proposal.ResponsibleStaff\
        or request.user == dist.Proposal.Track.Head:
        respondrights = True
    elif get_grouptype("3") in request.user.groups.all() or get_grouptype('6') in request.user.groups.all():
        pass
    else:
        raise PermissionDenied("You are not allowed to view these files")

    files = dist.files.all()
    return render(request, "professionalskills/listFiles.html", {"dist": dist, "files": files, "respond" : respondrights, 'edit': editrights})


@group_required('type3staff', 'type6staff')
def mailOverDueStudents(request):
    """
    Mail students that didn't handin file before the deadline

    :param request:
    :return:
    """
    if get_timephase_number() < 6:
        raise PermissionDenied('Mailing students for PRVs is not possible in this timephase')

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
                        'template' : 'email/overdueprvstudent.html',
                        'email'    : dist.Student.email,
                        'subject'  : 'Overdue PRV delivery',
                        'context'  : {
                            'student' : dist.Student,
                            'project' : dist.Proposal,
                            'types'   : missingtypes,
                        }
                    })

            EmailThreadMultipleTemplate(mails).start()

            return render(request, "support/emailProgress.html")
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        "form": form,
        "formtitle": "Confirm mailing overdue students",
        "buttontext": "Confirm"
    })


@group_required('type1staff', 'type2staff')
@can_access_professionalskills
def respondFile(request, pk):
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
                send_mail('Prv Feedback', 'email/prvresponse.html', {
                    'student' : fileobj.Distribution.Student,
                    'status' : form.cleaned_data['Status'],
                    'explanation' : form.cleaned_data['Explanation'],
                    'type' : fileobj.Type.Name,
                }, fileobj.Distribution.Student.email, 'email/prvresponse.html')
            form.save()
            return render(request, 'base.html', {
                'Message' : 'Response saved!',
                'return' : 'support:liststudents',
            })
    else:
        form = StaffReponseForm(instance=responseobj)

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Respond to {} from {}'.format(fileobj.Type.Name, fileobj.Distribution.Student.get_full_name())
    })


@student_only()
def listOwnFiles(request):
    """
    Shows the list of files of a student. Files are attached to distributions-objects.
    This function calls the general file list function listStudentFiles with this student as argument.

    :param request:
    :return:
    """

    if get_timephase_number() < 5:
        raise PermissionDenied("Student files are not available in this phase")

    dist = get_object_or_404(Distribution, Student=request.user)
    return listStudentFiles(request, dist.pk)


@group_required('type3staff', 'type6staff')
def printPrvForms(request):
    """
    Export PDF of all distributed students

    :param request:
    :return:
    """
    if get_timephase_number() < 5:
        raise PermissionDenied('Students are not yet distributed to projects.')

    template = get_template('professionalskills/printPrvResults.html')
    pages = []
    for dstr in Distribution.objects.all():
        obj = {
            'student'   : dstr.Student,
            'proposal'  : dstr.Proposal,
            'files'     : StaffReponse.objects.filter(File__Distribution=dstr).order_by('File__Type__id'),
        }
        try:
            obj['room'] = dstr.presenationtimeslot.Presentations.AssessmentRoom
            obj['time'] =  dstr.presenationtimeslot.DateTime
        except:
            pass
        pages.append(obj)

    # return render(request, 'professionalskills/printPrvResults.html', {
    #     'pages' : pages,
    # })

    htmlblock = template.render({
        'pages' : pages
    })

    buffer = BytesIO()
    pisaStatus = pisa.CreatePDF(htmlblock.encode('utf-8'), dest=buffer, encoding='utf-8')
    buffer.seek(0)
    response = HttpResponse(buffer, 'application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prvs.pdf"'
    return response


@group_required('type3staff', 'type6staff')
def createGroup(request, pk=None):
    if request.method == 'POST':
        form = StudentGroupForm(request.POST)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message' : '{} created!'.format(obj),
            })
    else:
        if pk is not None:
            obj = StudentGroup(PRV=get_object_or_404(FileType, pk=pk))
            form = StudentGroupForm(instance=obj)
        else:
            form = StudentGroupForm()
    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Create new Group',
        'buttontext' : 'Create'
    })


@group_required('type3staff', 'type6staff')
def editGroup(request, pk):
    obj = get_object_or_404(StudentGroup, pk=pk)
    if request.method == 'POST':
        form = StudentGroupForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message' : '{} saved!'.format(obj),
            })
    else:
        form = StudentGroupForm(instance=obj)
    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Edit Group',
        'buttontext' : 'Save'
    })


@group_required('type3staff', 'type6staff')
def listGroups(request, pk):
    PRV = get_object_or_404(FileType, pk=pk)
    return render(request, 'professionalskills/listAllGroups.html', {
        'groups' : PRV.groups.all(),
        'PRV' : PRV
    })


@group_required('type3staff', 'type6staff')
def listGroupMembers(request, pk):
    group = get_object_or_404(StudentGroup, pk=pk)
    return render(request, 'GenericList.html', {
        'items' : group.Members.all(),
        'title' : 'Members of group {}'.format(group),
    })


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


@group_required('type3staff', 'type6staff')
def assignStudents(request, pk):
    PRV = get_object_or_404(FileType, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            if PRV.groups.all().aggregate(Sum('Max'))['Max__sum'] < get_all_students().count():
                return render(request, 'base.html', {
                    'Message' : 'Groups capacity not sufficient'
                })
            for group in PRV.groups.all():
                group.Members.clear()
                group.save()
            students = list(get_all_students())
            totalstudents = len(students)
            random.shuffle(students)
            groups = list(PRV.groups.all())
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
                'Message' : 'Students divided over the groups'
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm reshuffling students for {}'.format(PRV),
        'buttontext' : 'Confirm'
    })


@student_only()
def switchGroup(request, frompk, topk):
    fromgroup = get_object_or_404(StudentGroup, pk=frompk)
    togroup = get_object_or_404(StudentGroup, pk=topk)

    if fromgroup not in request.user.studentgroups.all():
        return HttpResponseBadRequest('User not in from group')

    fromgroup.Members.remove(request.user)
    togroup.Members.add(request.user)
    togroup.save()
    fromgroup.save()

    return render(request, 'base.html', {
        'Message' : 'Switched to group {}'.format(togroup),
        'return' : 'professionalskills:listowngroups',
    })


@student_only()
def listOwnGroups(request):
    if request.method == 'POST':
        for g in request.user.studentgroups.all():
            f = StudentGroupChoice(request.POST, initial={'Group': g}, prefix=str(g.PRV.pk), PRV=g.PRV)
            if f.is_valid():
                try:
                    switchGroup(request, g.pk, f.cleaned_data['Group'].pk)
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
        f = StudentGroupChoice(initial={'Group' : g}, prefix=str(g.PRV.pk), PRV=g.PRV)
        groups.append((g, f))
    return render(request, 'professionalskills/listAllOwnGroups.html', {
        'groups' : groups
    })