import json
from datetime import date, datetime

from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models import Q, F
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from htmlmin.decorators import not_minified_response

from BepMarketplace.decorators import group_required
from distributions.utils import get_distributions
from general_form import ConfirmForm
from general_mail import EmailThreadTemplate, mail_track_heads_pending, send_mail
from general_model import GroupOptions, print_list
from general_view import get_all_students, get_all_staff, get_grouptype
from index.models import Track, UserMeta
from osirisdata.data import osirisData
from proposals.models import Proposal
from proposals.utils import get_all_proposals
from results.models import GradeCategory
from support import check_content_policy
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number
from .exports import get_list_students_xlsx, get_list_staff_xlsx, get_list_distributions_xlsx, get_list_proposals_xlsx
from .forms import ChooseMailingList, PublicFileForm, OverRuleUserMetaForm, UserGroupsForm, \
    CapacityGroupAdministrationForm
from .models import CapacityGroupAdministration, PublicFile


###############
# Distributions#
###############


@group_required("type3staff", "type6staff")
def list_applications_distributions(request):
    """
    Show a list of all active proposals with the applications and possibly distributions of students.
    Used for support staff as an overview.
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

    return render(request, 'support/listApplicationsDistributions.html', {"proposals": projects})


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


#########
# Mailing#
#########


#        (1, 'All users (danger)'),
#        (2, 'type1 staff'),
#        (3, 'type2 staff'),
#        (4, 'type2 staff unverified'),
#        (5, 'all type2 staff'),
#        (6, 'all staff'),
#        (7, 'staff with non finished proposal'),
#        (8, 'type3 staff'),
#        (9, 'all students on marketplace'),
#        (10, 'all students on marketplace 10ects'),
#        (11, 'all students on marketplace 15ects'),
@group_required('type3staff')
def mailing(request):
    """

    :param request:
    :return:
    """
    options = (
        ('all', 'All users'),
        ('type1', 'Type1 staff'),
        ('type2', 'Type2 staff'),
        ('type2un', 'Type2 staff unverified'),
        ('type2', 'All type2 staff'),
        ('staffnonfinishedprop', 'Staff with non finished proposal'),
        ('type3', 'Type3 staff'),
        ('osirisstudents', 'All students enrolled on osiris'),
        ('allstudents', 'All students on marketplace'),
        ('10ectsstud', 'Students on marketplace 10ECTS'),
        ('15ectsstud', 'Students on marketplace 15ECTS'),
        ('nostudprof', 'Professors with no students'),
        ('staffdistr', 'Staff with distributed students'),
    )

    if request.method == 'POST':
        form = ChooseMailingList(request.POST, options=options)
        if form.is_valid():
            recipients = set()

            # iterate through all selected users
            if form.cleaned_data['people_all']:
                # users
                for user in list(get_all_students()) + list(get_all_staff()):
                    recipients.add(user)
            if form.cleaned_data['people_type1']:
                # all type1staff
                for user in get_all_staff().filter(groups=get_grouptype("1")):
                    recipients.add(user)
            if form.cleaned_data['people_type2']:
                # type2staff
                for user in get_all_staff().filter(groups=get_grouptype("2")):
                    recipients.add(user)
            if form.cleaned_data['people_type2un']:
                # type2unverifiedstaff
                for user in get_all_staff().filter(groups=get_grouptype("2u")):
                    recipients.add(user)
            if form.cleaned_data['people_staffnonfinishedprop']:
                # staff with projects of stats < 3
                props = get_all_proposals().filter(Status__lt=3)
                for prop in props:
                    recipients.add(prop.ResponsibleStaff)
                    for ass in prop.Assistants.all():
                        recipients.add(ass)
            if form.cleaned_data['people_type3']:
                # type3staff
                for user in get_all_staff().filter(groups=get_grouptype("3")):
                    recipients.add(user)
            if form.cleaned_data['people_osirisstudents']:
                # students on osiris
                data = osirisData()
                for email in data.getallEmail():
                    recipients.add(email)
            if form.cleaned_data['people_allstudents']:
                # all students on marketplace
                for user in get_all_students():
                    recipients.add(user)
            if form.cleaned_data['people_10ectsstud']:
                # all students marketplace 10ects
                for user in get_all_students().filter(usermeta__EnrolledExt=False):
                    recipients.add(user)
            if form.cleaned_data['people_15ectsstud']:
                # all students marketplace 15ects
                for user in get_all_students().filter(usermeta__EnrolledExt=True):
                    recipients.add(user)
            if form.cleaned_data['people_nostudprof']:
                # professors with no students
                props = get_all_proposals().filter(distributions__isnull=True).distinct()
                for prop in props:
                    recipients.add(prop.ResponsibleStaff)
            if form.cleaned_data['people_staffdistr']:
                # staff with students
                props = get_all_proposals().filter(distributions__isnull=False).distinct()
                for prop in props:
                    recipients.add(prop.ResponsibleStaff)
                    for ass in prop.Assistants.all():
                        recipients.add(ass)

            # add support staff and study advisors
            for sup in list(get_grouptype("3").user_set.all()):
                recipients.add(sup)
            for sup in list(Group.objects.get(name='type5staff').user_set.all()):
                recipients.add(sup)
            for sup in list(Group.objects.get(name='type6staff').user_set.all()):
                recipients.add(sup)

            # always send copy to admins
            for user in User.objects.filter(is_superuser=True):
                recipients.add(user)

            # loop over all collected email addresses to create a message
            mails = []
            subject = form.cleaned_data['subject'] or 'message from support staff'
            for recipient in recipients:
                mails.append({
                    'template': 'email/supportstaff_email.html',
                    'email': recipient.email,
                    'subject': subject,
                    'context': {
                        'message': form.cleaned_data['message'],
                        'user': recipient,
                    }
                })
            EmailThreadTemplate(mails).start()
            return render(request, "support/email_progress.html")
    else:
        form = ChooseMailingList(options=options)

    return render(request, "GenericForm.html", {
        "form": form,
        "formtitle": "Send mailling list",
        "buttontext": "Send",
    })


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


#######
# Lists#
#######
@group_required('type3staff', 'type6staff')
def list_users(request):
    """
    List of all active users, including upgrade/downgrade button for staff and impersonate button for admins

    :param request:
    :return:
    """
    return render(request, "support/list_users.html", {
        "users": User.objects.all().prefetch_related('groups', 'usermeta', 'usermeta__TimeSlot'),
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

        if isinstance(obj, (User)):
            return obj.__str__()
        raise TypeError("Type %s not serializable" % type(obj))

    user = get_object_or_404(User, pk=pk)
    user_model = [[field.name, getattr(user, field.name)] for field in user._meta.fields if
                  field.name.lower() not in ['password', 'pass', 'key', 'secret', 'token', 'signature']]
    try:
        usermeta_model = [[field.name, getattr(user.usermeta, field.name)] for field in user.usermeta._meta.fields]
    except:
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
        print(ds)
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
    List all staff with a distributed proposal

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
        pt1 = s.proposalsresponsible.count()
        pt2 = s.proposals.count()
        pts = pt1 + pt2
        dt1 = nint(s.proposalsresponsible.all().annotate(Count('distributions')).aggregate(Sum('distributions__count'))[
                       'distributions__count__sum'])
        dt2 = nint(s.proposals.all().annotate(Count('distributions')).aggregate(Sum('distributions__count'))[
                       'distributions__count__sum'])
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

    return render(request, 'proposals/ProposalsCustomList.html',
                  {"title": "Proposals from " + user.usermeta.get_nice_name(), "proposals": projects})


@not_minified_response
@group_required("type3staff")
def list_staff_xlsx(request):
    """
    Same as supportListStaff but as XLSX
    """
    staff = get_all_staff().filter(Q(groups=get_grouptype("2")) | Q(groups=get_grouptype("1")))
    file = get_list_staff_xlsx(staff)
    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename=marketplace-staff-list.xlsx'
    return response


@group_required('type3staff')
def list_non_full_proposals(request):
    """
    Show page with button to download excel with non full proposals of a timeslot.

    :param request:
    :return:
    """
    return render(request, "support/non_full_proposals.html", {'timeslots': TimeSlot.objects.all()})


@not_minified_response
@group_required('type3staff')
def list_non_full_proposals_xlsx(request, timeslot):
    """
    Export excel of all proposals with space left.

    :param request:
    :param timeslot: The timeslot to get proposals from.
    """
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    props = Proposal.objects.annotate(num_distr=Count('distributions')).filter(TimeSlot=ts
                                                                               , num_distr__lt=F(
            'NumstudentsMax')).order_by('Title')

    file = get_list_proposals_xlsx(props)
    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename=non-full-proposals-{}.xlsx'.format(ts.Name)
    return response


@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def list_students(request):
    """
    For support staff, responsibles and assistants to view their students.
    List all students with distributions that the current user is allowed to see.
    Including a button to view the students files.
    In later timephase shows the grades as well.

    :param request:
    :return:
    """

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
    cats = GradeCategory.objects.filter(TimeSlot=get_timeslot())
    # des = get_distributions(request.user)
    des = get_distributions(request.user).select_related('Proposal__ResponsibleStaff',
                                                         'Proposal__Track',
                                                         'Student__usermeta', ).prefetch_related(
        'results__Category',
        'Proposal__Assistants')
    deslist = []
    # make grades
    for d in des:
        reslist = []
        for c in cats:
            try:
                reslist.append(d.results.get(Category=c).Grade)
            except:
                reslist.append('-')
        deslist.append([d, reslist])
    return render(request, "support/listDistributedStudents.html", {'des': deslist,
                                                                    'typ': cats,
                                                                    'show_grades': show_grades,
                                                                    'hide_sidebar': True})


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


@group_required('type4staff')
def list_group_projects(request):
    """
    List all proposals of a group.

    :param request:
    :return:
    """
    obj = get_object_or_404(CapacityGroupAdministration, Members__id=request.user.id)
    props = get_all_proposals(old=True).filter(Group=obj.Group)
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals": props,
        "title": "Proposals of My Group"
    })


@group_required('type5staff')
def list_studyadvisor_projects(request):
    """
    List all proposals for the studyadvisor, so includes old and private ones

    :param request:
    :return:
    """
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals": get_all_proposals(old=True),
        "title": "All proposals in system"
    })


@group_required('type3staff', 'type6staff')
def list_private_projects(request):
    """
    List all private proposals.

    :param request:
    :return:
    """
    props = get_all_proposals().filter(Private__isnull=False).distinct()
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals": props,
        "title": "All private proposals",
        "private": True
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


@group_required('type3staff')
def capacity_group_administration(request):
    """
    Used to to attach users to a research group as administration of that group.

    :param request:
    """
    if request.method == 'POST':
        form = CapacityGroupAdministrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "base.html", {
                "Message": "Capacity Group administration updated",
                "return": "support:capacitygroupadministration",
            })
    else:
        form = CapacityGroupAdministrationForm()

    return render(request, "support/capacity_group_administration.html", {
        "form": form,
        "formtitle": "Capacity Group Administrators",
        "buttontext": "Save",
    })


#
# @group_required('type3staff')
# def upgrade_user(request, pk):
#     """
#     Upgrade a user from type2staff to type1staff
#
#     :param request:
#     :param pk: id of the user.
#     :return:
#     """
#     usr = get_object_or_404(User, pk=pk)
#
#     # verify type 2 unverified
#     if get_grouptype("2u") in usr.groups.all():
#         if get_grouptype("2") in usr.groups.all():
#             usr.groups.remove(get_grouptype("2"))
#         if get_grouptype("2u") in usr.groups.all():
#             usr.groups.remove(get_grouptype("2u"))
#         usr.groups.add(get_grouptype("2"))
#         usr.save()
#         return render(request, "base.html", {
#             "Message": "Type2staff unverifed is now verified.",
#             "return": "support:listusers"
#         })
#
#     if not get_grouptype("2") in usr.groups.all():
#         return render(request, "base.html", {
#             "Message": "Only type2staff can be upgraded.",
#             "return": "support:listusers"
#         })
#
#     if get_grouptype("3") in usr.groups.all():
#         return render(request, "base.html", {
#             "Message": "User is supportstaff!",
#             "return": "support:listusers"
#         })
#
#     if get_grouptype("1") not in usr.groups.all():
#         if get_grouptype("2") in usr.groups.all():
#             usr.groups.remove(get_grouptype("2"))
#         if get_grouptype("2u") in usr.groups.all():
#             # this line should never hit. Just to be sure.
#             usr.groups.remove(get_grouptype("2u"))
#         usr.groups.add(get_grouptype("1"))
#         usr.save()
#
#     else:
#         return render(request, "base.html", {
#             "Message": "User is already upgraded!",
#             "return": "support:listusers"
#         })
#
#     if cache.has_key('listusersbodyhtml'):
#         cache.delete('listusersbodyhtml')
#     if cache.has_key('listusersbodyhtmladmin'):
#         cache.delete('listusersbodyhtmladmin')
#
#     return render(request, "base.html", {
#         "Message": "User upgraded!",
#         "return": "support:listusers"
#     })
#
#
# @group_required('type3staff')
# def downgrade_user(request, pk):
#     """
#     Change a user from type1staff to type2staff
#
#     :param request:
#     :param pk: id of the staff user.
#     :return:
#     """
#     usr = get_object_or_404(User, pk=pk)
#
#     if not get_grouptype("1") in usr.groups.all():
#         return render(request, "base.html", {
#             "Message": "Only type1staff can be downgraded.",
#             "return": "support:listusers"
#         })
#
#     if get_grouptype("3") in usr.groups.all():
#         return render(request, "base.html", {
#             "Message": "User is support staff!",
#             "return": "support:listusers"
#         })
#
#     if get_grouptype("2") not in usr.groups.all() and get_grouptype("2u") not in usr.groups.all():
#         if get_grouptype("1") in usr.groups.all():
#             usr.groups.remove(get_grouptype("1"))
#         usr.groups.add(get_grouptype("2"))
#         usr.save()
#
#     if cache.has_key('listusersbodyhtml'):
#         cache.delete('listusersbodyhtml')
#     if cache.has_key('listusersbodyhtmladmin'):
#         cache.delete('listusersbodyhtmladmin')
#
#     return render(request, "base.html", {
#         "Message": "User downgraded!",
#         "return": "support:listusers"
#     })


#######
# Other#
#######

@group_required('type1staff', 'type2staff', 'type3staff', 'type4staff', 'type5staff')
def stats(request):
    """
    Statistics about number of proposals, with breakdown per group.

    :param request:
    :return:
    """
    groupcount = {}
    trackcount = {}
    statuscount = [
        get_all_proposals().filter(Status=1).count(),
        get_all_proposals().filter(Status=2).count(),
        get_all_proposals().filter(Status=3).count(),
        get_all_proposals().filter(Status=4).count()
    ]

    for group in GroupOptions:
        groupcount[group[0]] = get_all_proposals().filter(Group=group[0]).count()

    for track in Track.objects.all():
        trackcount[track.__str__()] = get_all_proposals().filter(Track=track).count()

    return render(request, "support/stats.html", {
        "proposalcount": get_all_proposals().count(),
        "usercount": get_all_students().count() + get_all_staff().count(),
        "privatecount": get_all_proposals().filter(Private__isnull=False).count(),
        "groupcount": groupcount,
        "statuscount": statuscount,
        "trackcount": trackcount,
        "mincapacity": get_all_proposals().aggregate(Sum('NumstudentsMin'))['NumstudentsMin__sum'],
        "maxcapacity": get_all_proposals().aggregate(Sum('NumstudentsMax'))['NumstudentsMax__sum']
    })


@group_required('type3staff')
def content_policy(request):
    """
    List of proposal description/assignment texts that do not met the expected text.
    Example of a policy violation is an email address in a proposal description.

    :param request:
    """
    data = {
        'pattern_violations': check_content_policy.cpv_regex(),
        'length_violations': check_content_policy.cpv_length(),
        'diff_violations': check_content_policy.cpv_diff(),
        'pattern_policies': check_content_policy.content_policies,
        'length_requirements': check_content_policy.length_requirements.items(),
    }
    return render(request, 'support/content_policy_violations.html', data)


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
