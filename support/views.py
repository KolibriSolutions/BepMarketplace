import json
import json
import logging
from datetime import date, datetime

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum, F, Q
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from htmlmin.decorators import not_minified_response

from distributions.utils import get_distributions
from general_form import ConfirmForm
from general_mail import EmailThreadTemplate, mail_track_heads_pending, send_mail
from general_model import print_list
from general_view import get_all_staff, get_grouptype
from index.decorators import group_required
from index.models import Track, UserMeta
from presentations.exports import get_list_presentations_xlsx
from presentations.models import PresentationSet, PresentationTimeSlot
from proposals.models import Proposal
from proposals.utils import get_all_proposals
from results.models import CategoryResult, GradeCategory
from students.models import Distribution, TimeSlot
from timeline.utils import get_timeslot, get_timephase_number, get_recent_timeslots
from .exports import get_list_students_xlsx, get_list_distributions_xlsx, get_list_projects_xlsx
from .forms import ChooseMailingList, PublicFileForm, OverRuleUserMetaForm, UserGroupsForm, \
    GroupadministratorEdit, CapacityGroupForm
from .models import GroupAdministratorThrough, PublicFile, CapacityGroup, mail_staff_options, mail_student_options, MailTemplate, Mailing

logger = logging.getLogger('django')

#########
# Mailing#
#########
@group_required('type3staff')
def list_mailing_templates(request):
    return render(request, 'support/list_mail_templates.html', {'templates': MailTemplate.objects.all()})


@group_required('type3staff')
def delete_mailing_template(request, pk):
    """

    :param request:
    :param pk: pk of template
    :return:
    """
    name = 'Mailing template'
    obj = get_object_or_404(MailTemplate, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            obj.delete()
            return render(request, 'base.html', {
                'Message': '{} deleted.'.format(name),
                'return': 'support:mailingtemplates'})
    else:
        form = ConfirmForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Delete {}?'.format(name),
        'buttontext': 'Delete'
    })


@group_required('type3staff')
def mailing(request, pk=None):
    """
    Mailing list to mail users.

    :param request:
    :param pk: optional key of a mailing template
    :return:
    """
    if request.method == 'POST':
        form = ChooseMailingList(request.POST, staff_options=mail_staff_options, student_options=mail_student_options, )
        if form.is_valid():
            recipients_staff = set()
            recipients_students = set()
            # staff
            if form.cleaned_data['SaveTemplate']:
                t = MailTemplate(
                    RecipientsStaff=json.dumps(form.cleaned_data['Staff']),
                    RecipientsStudents=json.dumps(form.cleaned_data['Students']),
                    Message=form.cleaned_data['Message'],
                    Subject=form.cleaned_data['Subject'],
                )
                t.save()

            ts = form.cleaned_data['TimeSlot']
            for s in form.cleaned_data['Staff']:
                try:
                    # staff selected by group
                    recipients_staff.update(Group.objects.get(name=s).user_set.all())
                    if s not in ['type3staff', 'type4staff', 'type5staff', 'type6staff']:
                        # if user group is not a support type, mail only users with project in this year.
                        for staff in list(recipients_staff):
                            if not staff.proposalsresponsible.filter(TimeSlot=ts).exists() and not staff.proposals.filter(TimeSlot=ts).exists():
                                # user has no project in the selected timeslots.
                                recipients_staff.remove(staff)
                except Group.DoesNotExist:
                    # not a group object, staff selected by custom options.
                    projs = get_all_proposals(old=True).filter(
                        TimeSlot=ts)
                    if s == 'staffnonfinishedproj':
                        for proj in projs.filter(Status__lt=3).distinct():
                            recipients_staff.add(proj.ResponsibleStaff)
                            recipients_staff.update(proj.Assistants.all())
                    elif s == 'distributedstaff':
                        for proj in projs.filter(distributions__isnull=False).distinct():
                            recipients_staff.add(proj.ResponsibleStaff)
                            recipients_staff.update(proj.Assistants.all())
                    elif s == 'staffnostudents':
                        for proj in projs.filter(distributions__isnull=True).distinct():
                            recipients_staff.add(proj.ResponsibleStaff)
                            recipients_staff.update(proj.Assistants.all())
                    elif s == 'assessors':
                        dists = Distribution.objects.filter(TimeSlot=ts).distinct()
                        for d in dists:
                            try:
                                recipients_staff.update(d.presentationtimeslot.Presentations.Assessors.all())
                            except PresentationTimeSlot.DoesNotExist:
                                continue
                        recipients_staff.update(User.objects.filter(tracks__isnull=False))  # add trackheads
            # students
            students = User.objects.filter(
                Q(usermeta__TimeSlot=ts) &
                Q(usermeta__EnrolledBEP=True) &
                Q(groups=None))
            for s in form.cleaned_data['Students']:
                if s == 'all':
                    recipients_students.update(students)
                elif s == '10ectsstd':
                    recipients_students.update(students.filter(usermeta__EnrolledExt=False))
                elif s == '15ectsstd':
                    recipients_students.update(students.filter(usermeta__EnrolledExt=True))
                elif s == 'distributedstd':
                    recipients_students.update(students.filter(
                        distributions__isnull=False,
                        distributions__TimeSlot=ts).distinct())

            # always send copy to admins
            for user in User.objects.filter(is_superuser=True):
                recipients_staff.add(user)
            # always send copy to self
            if request.user not in recipients_students or \
                    request.user not in recipients_staff:
                recipients_staff.update([request.user])

            mailing_obj = Mailing(
                Subject=form.cleaned_data['Subject'],
                Message=form.cleaned_data['Message'],
            )
            mailing_obj.save()
            mailing_obj.RecipientsStaff.set(recipients_staff)
            mailing_obj.RecipientsStudents.set(recipients_students)
            context = {
                'form': ConfirmForm(initial={'confirm': True}),
                'template': form.cleaned_data['SaveTemplate'],
                'mailing': mailing_obj,
            }
            return render(request, "support/email_confirm.html",
                          context=context)
    else:
        initial = None
        if pk:
            template = get_object_or_404(MailTemplate, pk=pk)
            initial = {
                'Message': template.Message,
                'Subject': template.Subject,
                'Staff': json.loads(template.RecipientsStaff),
                'Students': json.loads(template.RecipientsStudents),
            }
        form = ChooseMailingList(initial=initial, staff_options=mail_staff_options, student_options=mail_student_options)
    return render(request, "GenericForm.html", {
        "form": form,
        "formtitle": "Send mailing list",
        "buttontext": "Go to confirm",
    })


@group_required('type3staff')
def confirm_mailing(request):
    if request.method == 'POST':
        mailing_obj = get_object_or_404(Mailing, id=request.POST.get('mailingid', None))
        form = ConfirmForm(request.POST)
        if form.is_valid():
            # loop over all collected email addresses to create a message
            mails = []
            for recipient in mailing_obj.RecipientsStaff.all() | mailing_obj.RecipientsStudents.all():
                mails.append({
                    'template': 'email/supportstaff_email.html',
                    'email': recipient.email,
                    'subject': mailing_obj.Subject,
                    'context': {
                        'message': mailing_obj.Message,
                        'name': recipient.usermeta.get_nice_name(),
                    }
                })
            EmailThreadTemplate(mails).start()
            mailing_obj.Sent = True
            mailing_obj.save()
            return render(request, "support/email_progress.html")
        raise PermissionDenied('The confirm checkbox was unchecked.')
    raise PermissionDenied("No post data supplied!")


@group_required('type3staff')
def mail_track_heads(request):
    """
    Mail all track heads with their actions

    :param request:
    :return:
    """
    if get_timephase_number() > 2:
        return render(request, "base.html", {"Message": "Only possible in first two phases"})
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            mail_track_heads_pending()
            return render(request, "base.html", {"Message": "Track Heads mailed!"})
    else:
        form = ConfirmForm()

    trackstats = {}
    for track in Track.objects.all():
        trackstats[str(track)] = {
            'pending': get_all_proposals().filter(Q(Status=3) & Q(Track=track)).count(),
            'head': track.Head.email,
        }
    return render(request, "support/TrackHeadSendConfirm.html", {'trackstats': trackstats, 'form': form})


@group_required('type3staff')
def groupadministrators_form(request):
    """
    Set group administrators, same way as in mastermp.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = GroupadministratorEdit(request.POST)
        if form.is_valid():
            administratorusergroup = Group.objects.get(name='type4staff')
            group = form.cleaned_data['group']
            for u in form.cleaned_data['readmembers']:
                g, created = GroupAdministratorThrough.objects.get_or_create(Group=group, User=u)
                g.Super = False
                g.save()
                u.groups.add(administratorusergroup)
                u.save()
            for u in form.cleaned_data['writemembers']:
                g, created = GroupAdministratorThrough.objects.get_or_create(Group=group, User=u)
                g.Super = True
                g.save()
                u.groups.add(administratorusergroup)
                u.save()
            for g in GroupAdministratorThrough.objects.filter(Group=group):
                if g.User not in form.cleaned_data['readmembers'] and g.User not in form.cleaned_data['writemembers']:
                    g.delete()
                    if g.User.administratoredgroups.count() == 0:
                        g.User.groups.remove(administratorusergroup)
                        g.User.save()
            return render(request, 'base.html', {
                'Message': 'Administrators saved!',
                'return': 'support:groupadministratorsform',
            })
    else:
        form = GroupadministratorEdit()

    return render(request, 'support/groupadministrators.html', {
        'form': form,
        'formtitle': 'Set Group Administrators',
        'buttontext': 'save',
    })


@group_required('type3staff')
def add_capacity_group(request):
    if request.method == 'POST':
        form = CapacityGroupForm(request.POST)
        if form.is_valid():
            obj = form.save()
            return render(request, 'base.html', {
                'Message': 'Capacity group {} added.'.format(obj.FullName),
                'return': 'support:listcapacitygroups'
            })
    else:
        form = CapacityGroupForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add new Capacity Group',
        'buttontext': 'Add'
    })


@group_required('type3staff')
def edit_capacity_group(request, pk):
    obj = get_object_or_404(CapacityGroup, pk=pk)

    if request.method == "POST":
        form = CapacityGroupForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                'Message': 'Group {} saved.'.format(obj),
                'return': 'support:listcapacitygroups',
            })
    else:
        form = CapacityGroupForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit Group',
        'buttontext': 'Save'
    })


@group_required('type3staff')
def delete_capacity_group(request, pk):
    obj = get_object_or_404(CapacityGroup, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            obj.delete()
            return render(request, 'base.html', {
                'Message': 'Capacity group {} deleted.'.format(obj),
                'return': 'support:listcapacitygroups'
            })
    else:
        form = ConfirmForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm deletion of {}'.format(obj),
        'buttontext': 'Delete'
    })


#######
# Lists#
#######

def list_capacity_groups(request):
    """
    List all capacity groups, edit buttons for support staff

    :param request:
    :return:
    """
    return render(request, 'support/list_capacitygroups.html', {
        'groups': CapacityGroup.objects.all().select_related('Head'),
        'hide_sidebar': True,
        'MASTERMP': getattr(settings, 'MASTERMARKETPLACE_URL', False),  # for detaillink to mastermp.
    })


@group_required('type3staff', 'type6staff')
def list_users(request):
    """
    List of all active users, including upgrade/downgrade button for staff and impersonate button for admins

    :param request:
    :return:
    """
    return render(request, "support/list_users.html", {
        "users": User.objects.all().prefetch_related('groups', 'usermeta', 'usermeta__TimeSlot', 'administratoredgroups'),
        'hide_sidebar': True,
    })


@group_required('type3staff')
def usermeta_overrule(request, pk):
    """

    :param request:
    :param pk:
    :return:
    """
    usr = get_object_or_404(User, pk=pk)
    obj = get_object_or_404(UserMeta, pk=usr.usermeta.id)
    if request.method == "POST":
        form = OverRuleUserMetaForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            obj.Overruled = True
            obj.save()

            return render(request, 'base.html', {
                'Message': 'UserMeta saved!'
            })
    else:
        form = OverRuleUserMetaForm(instance=obj)

    return render(request, 'GenericForm.html', {
        'formtitle': 'Overrule UserMeta',
        'form': form,
    })


@group_required('type3staff')  # might be added to profile in the future.
def user_info(request, pk):
    """
    Return information and privacy data of given user.

    :param request:
    :param pk:
    :return:
    """

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, User):
            return obj.__str__()
        raise TypeError("Type %s not serializable" % type(obj))

    user = get_object_or_404(User, pk=pk)
    user_model = [[field.name, getattr(user, field.name)] for field in user._meta.fields if
                  field.name.lower() not in ['password', 'pass', 'key', 'secret', 'token', 'signature']]
    try:
        usermeta_model = [[field.name, getattr(user.usermeta, field.name)] for field in user.usermeta._meta.fields]
    except UserMeta.DoesNotExist:
        usermeta_model = []
    related = []
    for obj in user._meta.related_objects + user._meta.many_to_many:
        if hasattr(user, obj.name):
            try:
                related.append([obj.name, [obj2.__str__() for obj2 in getattr(user, obj.name).all()]])
            except:
                related.append([obj.name, [getattr(user, obj.name).__str__()]])
        else:
            related.append([obj.name, []])
    distribution = []
    if user.groups.exists():
        ds = []
        for p in user.proposals.all():
            ds += list(p.distributions.all())
        for p in user.proposalsresponsible.all():
            ds += list(p.distributions.all())
    else:  # student
        ds = user.distributions.all()
    for d in ds:
        for obj in d._meta.related_objects + d._meta.many_to_many:
            if hasattr(d, obj.name):
                try:
                    distribution.append([obj.name, [obj2.__str__() for obj2 in getattr(d, obj.name).all()]])
                except:
                    distribution.append([obj.name, [getattr(d, obj.name).__str__()]])
            else:
                distribution.append([obj.name, []])
    return render(request, 'index/user_info.html', {
        'view_user': user,
        'user_model': user_model,
        'usermeta_model': usermeta_model,
        'related': related,
        'distribution': distribution,
        'json': json.dumps(
            {
                'user_model': user_model,
                'usermeta_model': usermeta_model,
                'related': related,
                'distribution': distribution
            }, default=json_serial),
    })


@group_required('type3staff', 'type6staff')
def list_staff(request):
    """
    List all staff with a distributed projects

    :param request:
    :return:
    """

    def nint(nr):
        """
        :param <int> nr:
        :return:
        """
        if nr is None:
            return 0
        else:
            return int(nr)

    staff = get_all_staff().filter(Q(groups=get_grouptype("2")) | Q(groups=get_grouptype("1"))).prefetch_related(
        'proposalsresponsible', 'proposals')
    se = []
    for s in staff:
        p1 = s.proposalsresponsible.filter(TimeSlot=get_timeslot())
        p2 = s.proposals.filter(TimeSlot=get_timeslot())
        pt1 = p1.count()
        pt2 = p2.count()
        pts = pt1 + pt2
        dt1 = nint(p1.annotate(Count('distributions')).aggregate(Sum('distributions__count'))['distributions__count__sum'])
        dt2 = nint(p2.annotate(Count('distributions')).aggregate(Sum('distributions__count'))['distributions__count__sum'])
        dts = dt1 + dt2
        se.append({"user": s, "pt1": pt1, "pt2": pt2, "pts": pts, "dt1": dt1, "dt2": dt2, "dts": dts})
    return render(request, 'support/list_staff.html', {"staff": se})


@group_required('type3staff')
def list_staff_projects(request, pk):
    """
    List all proposals of a staff member
    """
    user = get_all_staff().get(id=pk)
    projects = user.proposalsresponsible.all() | user.proposals.all()
    projects = projects.select_related('ResponsibleStaff', 'Track', 'TimeSlot'). \
        prefetch_related('Assistants', 'distributions', 'applications')

    return render(request, 'proposals/list_projects_custom.html',
                  {"title": "Proposals from " + user.usermeta.get_nice_name(), "proposals": projects})


# Does not filter on timeslot, depricated.
# @not_minified_response
# @group_required("type3staff")
# def list_staff_xlsx(request):
#     """
#     Same as supportListStaff but as XLSX
#     """
#     staff = get_all_staff().filter(Q(groups=get_grouptype("2")) | Q(groups=get_grouptype("1")))
#     file = get_list_staff_xlsx(staff)
#     response = HttpResponse(content=file)
#     response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     response['Content-Disposition'] = 'attachment; filename=marketplace-staff-list.xlsx'
#     return response

@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def list_students(request, timeslot):
    """
    For support staff, responsibles and assistants to view their students.
    List all students with distributions that the current user is allowed to see.
    Including a button to view the students files.
    In later timephase shows the grades as well.

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
        else:
            show_grades = False
    else:
        # historic view of distributions. Hide grades, as they might have changed outside the system.
        show_grades = False

    des = get_distributions(request.user, ts).select_related('Proposal__ResponsibleStaff',
                                                             'Proposal__Track',
                                                             'Student__usermeta').prefetch_related('Proposal__Assistants')
    cats = None
    if show_grades:
        cats = GradeCategory.objects.filter(TimeSlot=get_timeslot())
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
    return render(request, "support/list_students.html", {'des': deslist,
                                                          'typ': cats,
                                                          'show_grades': show_grades,
                                                          'hide_sidebar': True,
                                                          'timeslots': get_recent_timeslots(),
                                                          'timeslot': ts,
                                                          'is_current': current_ts,
                                                          })


@not_minified_response
@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def list_students_xlsx(request):
    """
    Same as liststudents but as XLSX. The combination of students and grades is done in general_excel.

    :param request:
    """
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

    typ = GradeCategory.objects.filter(TimeSlot=get_timeslot())
    des = get_distributions(request.user)
    file = get_list_students_xlsx(des, typ)

    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename=students-grades.xlsx'
    return response


@group_required('type3staff')
def verify_assistants(request):
    """
    Page to let support staff give type2staffunverified the type2staff status.
    Can also be done using the userlist.

    :param request:
    :return:
    """
    accounts = list(get_grouptype("2u").user_set.all())
    return render(request, "support/verifyAccounts.html", {
        "accounts": accounts
    })


@group_required('type3staff')
def edit_user_groups(request, pk):
    """
    Change the groups of a given user.

    :param request:
    :param pk: user id
    :return:
    """
    usr = get_object_or_404(User, pk=pk)
    if not usr.groups.exists():
        if not usr.is_superuser:
            raise PermissionDenied("This user is a student. Students cannot have groups.")
    if get_grouptype("2u") in usr.groups.all():
        raise PermissionDenied("This user is not yet verified. Please verify first in the user list.")

    if request.method == "POST":
        form = UserGroupsForm(request.POST, instance=usr)
        if form.is_valid():
            if form.has_changed():
                # call print list here to force query execute
                old = print_list(usr.groups.all().values_list('name', flat=True))
                form.save()
                new = print_list(usr.groups.all().values_list('name', flat=True))
                send_mail("user groups changed", "email/user_groups_changed.html",
                          {'oldgroups': old,
                           'newgroups': new,
                           'user': usr},
                          usr.email)
                return render(request, 'base.html', {
                    'Message': 'User groups saved!',
                    'return': 'support:listusers',
                })
            return render(request, 'base.html', {
                'Message': 'No changes made.',
                'return': 'support:listusers',
            })
    else:
        form = UserGroupsForm(instance=usr)
    return render(request, 'support/user_groups_form.html', {
        'formtitle': 'Set user groups for {}'.format(usr.username),
        'form': form,
    })


@group_required("type3staff")
def toggle_disable_user(request, pk):
    """
    en/disable a user to prevent him/her from login

    :param request:
    :param pk:
    :return:
    """
    usr = get_object_or_404(User, pk=pk)
    usr.is_active = not usr.is_active
    usr.save()
    return redirect('support:listusers')


# deprecated due to osirisdata
# @group_required("type3staff")
# def ECTSForm(request):
#     """
#     Form to fill in the ECTS of students, this is done by administration staff.
#     ECTS are used for the automatic distribution. ECTS changes are send using websockets to consumers.py
#
#     :param request:
#     """
#     stds = get_all_students()
#     return render(request, 'support/ECTSForm.html', {'students': stds})

##############
# Public Files#
##############

@group_required('type3staff')
def add_file(request):
    """
    Upload a public file. These files will be visible on the index page after login.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = PublicFileForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            file = form.save(commit=False)
            file.User = request.user
            file.save()
            return render(request, "base.html",
                          {"Message": "File uploaded!", "return": "index:index"})
    else:
        form = PublicFileForm(request=request)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Upload a public file ', 'buttontext': 'Save'})


@group_required('type3staff')
def edit_file(request, pk):
    """
    Edit a public file. These files will be visible on the index page after login.

    :param request:
    :param pk: id of file.
    :return:
    """
    obj = get_object_or_404(PublicFile, pk=pk)
    if request.method == 'POST':
        form = PublicFileForm(request.POST, request.FILES, request=request, instance=obj)
        if form.is_valid():
            if form.has_changed():
                file = form.save(commit=False)
                file.User = request.user
                file.save()
                return render(request, "base.html",
                              {"Message": "File changed!", "return": "index:index"})
            return render(request, "base.html",
                          {"Message": "No changes made.", "return": "index:index"})
    else:
        form = PublicFileForm(request=request, instance=obj)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Edit public file ', 'buttontext': 'Save'})


@group_required('type3staff')
def edit_files(request):
    """
    Edit public files. Only for supportstaff
    These files are shown on the homepage for every logged in user.

    :param request:
    """
    form_set = modelformset_factory(PublicFile, form=PublicFileForm, can_delete=True, extra=0)
    qu = PublicFile.objects.filter(TimeSlot=get_timeslot())
    formset = form_set(queryset=qu)

    if request.method == 'POST':
        formset = form_set(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "File changes saved!", "return": "index:index"})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': 'All public uploaded files', 'buttontext': 'Save changes'})


@group_required('type3staff')
def delete_file(request, pk):
    """
    Delete a public file

    :param request:
    :param pk: pk of the proposal to delete
    :return:
    """
    obj = get_object_or_404(PublicFile, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            obj.delete()
            return render(request, "base.html", {"Message": "Public file removed!", "return": "index:index"})
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Confirm deleting public file {}'.format(obj),
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def history(request):
    """
    Show historic data and options to download data

    :param request:
    :return:
    """
    tss = TimeSlot.objects.filter(End__lte=datetime.now())
    return render(request, 'index/history.html', context={
        'timeslots': tss,
    })


@not_minified_response
@group_required("type3staff")
def history_download(request, timeslot, download):
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    if ts == get_timeslot() or ts.Begin > timezone.now().date():
        raise PermissionDenied("Downloads of the current and future timeslots are not allowed. Please use the regular menu entries.")
    if download == 'distributions':
        projects = Proposal.objects.filter(TimeSlot=ts, Status=4).distinct()
        file = get_list_distributions_xlsx(projects)
        response = HttpResponse(content=file)
        response['Content-Disposition'] = 'attachment; filename=marketplace-projects-distributions.xlsx'
    elif download == 'students':
        typ = GradeCategory.objects.filter(TimeSlot=ts)
        des = Distribution.objects.filter(TimeSlot=ts)
        file = get_list_students_xlsx(des, typ)
        response = HttpResponse(content=file)
        response['Content-Disposition'] = 'attachment; filename=students-grades.xlsx'
    elif download == 'presentations':
        sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts)
        if not sets:
            return render(request, "base.html",
                          {"Message": "There is nothing planned yet. Please plan the presentations first."})
        file = get_list_presentations_xlsx(sets)
        response = HttpResponse(content=file)
        response['Content-Disposition'] = 'attachment; filename=presentations-planning.xlsx'
    elif download == 'nonfull':
        projects = Proposal.objects.annotate(num_distr=Count('distributions')).filter(TimeSlot=ts, num_distr__lt=F('NumStudentsMax')).order_by('Title')
        file = get_list_projects_xlsx(projects)
        response = HttpResponse(content=file)
        response['Content-Disposition'] = 'attachment; filename=non-full-proposals-{}.xlsx'.format(ts.Name)
    else:
        raise PermissionDenied("Invalid options.")
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response

#######
# Cache#
#######
#
# @group_required('type3staff', 'type6staff')
# def list_users_clear_cache(request):
#     """
#     Clear cache for list users
#
#     :param request:
#     :return:
#     """
#     cache.delete('listusersbodyhtmladmin')
#     cache.delete('listusersbodyhtml')
#
#     return render(request, 'base.html', {'Message': 'Cache cleared for userlist', "return": "support:listusers"})
