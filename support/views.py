from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from render_block import render_block_to_string

import general_excel
import general_mail
from BepMarketplace.decorators import group_required
from general_form import ConfirmForm
from general_mail import EmailThread
from general_view import get_distributions, get_all_students, get_timephase_number, get_all_staff, get_all_proposals, get_grouptype, get_timeslot
from index.models import Track, UserMeta
from general_model import GroupOptions
from results.models import GradeCategory
from support import check_content_policy
from .forms import ChooseMailingList, FileAddForm, FileEditForm, OverRuleUserMetaForm
from .models import CapacityGroupAdministration, PublicFile


###############
#Distributions#
###############


@group_required("type3staff", "type6staff")
def supportListApplicationsDistributions(request):
    """
    Show a list of all active proposals with the applications and possibly distributions of students.
    Used for support staff as an overview.
    """
    if get_timephase_number() < 3:
        raise PermissionDenied("There are no applications yet")
    elif get_timephase_number() > 4:
        proposals = get_all_proposals().filter(Q(Status=4) & Q(distributions__isnull=False)).distinct()
    else:  # phase 3 & 4
        proposals = get_all_proposals().filter(Status=4)
    return render(request, 'support/listApplicationsDistributions.html', {"proposals": proposals})


@group_required("type3staff", "type6staff")
def supportListDistributionsXls(request):
    """
    Same as supportListApplications but as XLSX
    """
    if get_timephase_number() < 3:
        raise PermissionDenied("There are no applications yet")
    elif get_timephase_number() > 4:
        proposals = get_all_proposals().filter(Q(Status=4) & Q(distributions__isnull=False)).distinct()
    else:
        proposals = get_all_proposals().filter(Status=4)
    file = general_excel.listDistributionsXls(proposals)
    response = HttpResponse(content=file)
    response['Content-Disposition'] = 'attachment; filename=marketplace-projects-distributions.xlsx'
    return response


#########
#Mailing#
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
def mailinglist(request):
    options = (
        ('all', 'All users'),
        ('type1', 'Type1 staff'),
        ('type2', 'Type2 staff'),
        ('type2un', 'Type2 staff unverified'),
        ('type2', 'All type2 staff'),
        ('staffnonfinishedprop', 'Staff with non finished proposal'),
        ('type3', 'Type3 staff'),
        ('allstudents', 'All students on marketplace'),
        ('10ectsstud', 'Students on marketplace 10ECTS'),
        ('15ectsstud', 'Students on marketplace 15ECTS'),
        ('nostudprof', 'Professors with no students'),
        ('staffdistr', 'Staff with distributed students'),
    )

    if request.method == 'POST':
        form = ChooseMailingList(request.POST, options=options)
        if form.is_valid():
            emails = set()

            # iterate through all selected users
            if form.cleaned_data['people_all']:
                # users
                for user in list(get_all_students())+list(get_all_staff()):
                    emails.add(user.email)
            if form.cleaned_data['people_type1']:
                # all type1staff
                for user in get_all_staff().filter(groups=get_grouptype("1")):
                    emails.add(user.email)
            if form.cleaned_data['people_type2']:
                # type2staff
                for user in get_all_staff().filter(groups=get_grouptype("2")):
                    emails.add(user.email)
            if form.cleaned_data['people_type2un']:
                # type2unverifiedstaff
                for user in get_all_staff().filter(groups=get_grouptype("2u")):
                    emails.add(user.email)
            if form.cleaned_data['people_staffnonfinishedprop']:
                # staff with projects of stats < 3
                props = get_all_proposals().filter(Status__lt=3)
                for prop in props:
                    emails.add(prop.ResponsibleStaff.email)
                    for ass in prop.Assistants.all():
                        emails.add(ass.email)
            if form.cleaned_data['people_type3']:
                # type3staff
                for user in get_all_staff().filter(groups=get_grouptype("3")):
                    emails.add(user.email)
            if form.cleaned_data['people_allstudents']:
                # all students on marketplace
                for user in get_all_students():
                    emails.add(user.email)
            if form.cleaned_data['people_10ectsstud']:
                # all students marketplace 10ects
                for user in get_all_students().filter(usermeta__EnrolledExt=False):
                    emails.add(user.email)
            if form.cleaned_data['people_15ectsstud']:
                # all students marketplace 15ects
                for user in get_all_students().filter(usermeta__EnrolledExt=True):
                    emails.add(user.email)
            if form.cleaned_data['people_nostudprof']:
                # professors with no students
                props = get_all_proposals().filter(distributions__isnull=True).distinct()
                for prop in props:
                    emails.add(prop.ResponsibleStaff.email)
            if form.cleaned_data['people_staffdistr']:
                #staff with students
                props = get_all_proposals().filter(distributions__isnull=False).distinct()
                for prop in props:
                    emails.add(prop.ResponsibleStaff.email)
                    for ass in prop.Assistants.all():
                        emails.add(ass.email)

            # add support staff and study advisors
            for sup in list(get_grouptype("3").user_set.all()):
                emails.add(sup.email)
            for sup in list(Group.objects.get(name='type5staff').user_set.all()):
                emails.add(sup.email)
            for sup in list(Group.objects.get(name='type6staff').user_set.all()):
                emails.add(sup.email)

            context = {
                'message' : form.cleaned_data['message'],
            }
            if form.cleaned_data['subject'] != '':
                subject = form.cleaned_data['subject']
            else:
                subject = "email/supportstaff_email_subject.txt"
            EmailThread(subject, "email/supportstaff_email.html", context,
                        emails).start()
            return render(request, "support/emailProgress.html")
    else:
        form = ChooseMailingList(options=options)

    return render(request, "GenericForm.html", {
        "form" : form,
        "formtitle" : "Send mailling list",
        "buttontext" : "Send",
    })


@group_required('type3staff')
def mailTrackHeads(request):
    """
    Mail all track heads with their todo actions
    
    :param request: 
    :return: 
    """
    if get_timephase_number() > 2:
        return render(request, "base.html", {"Message" : "Only possible in first two phases"})
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            general_mail.MailTrackHeadsPending()
            return render(request, "base.html", {"Message" : "Track Heads mailed!"})
    else:
        form = ConfirmForm()

    trackstats = {}
    for track in Track.objects.all():
        trackstats[str(track)] = {
            'pending' : get_all_proposals().filter(Q(Status=3) & Q(Track=track)).count(),
            'head' : track.Head.email,
        }
    return render(request, "support/TrackHeadSendConfirm.html", {'trackstats':trackstats, 'form' : form})


#######
#Lists#
#######
@group_required('type3staff', 'type6staff')
def listUsers(request):
    """
    List of all active users, including upgrade/downgrade button for staff and impersonate button for admins

    :param request:
    :return:
    """
    if request.user.is_superuser:
        key = 'listusersbodyhtmladmin'
    else:
        key = 'listusersbodyhtml'
    bodyhtml = cache.get(key)
    if bodyhtml is None:
        bodyhtml = render_block_to_string('support/listUsers.html', 'body', {"users": User.objects.all(),
                                                                             "user": request.user})
        cache.set(key, bodyhtml, None)

    return render(request, "support/listUsers.html", {
        "bodyhtml": bodyhtml,
    })


@group_required('type3staff')
def usermetaOverrule(request, pk):
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


@group_required('type3staff', 'type6staff')
def listStaff(request):
    """
    List all staff with a distributed proposal

    :param request:
    :return:
    """
    def nint(nr):
        if nr is None:
            return 0
        else:
            return int(nr)

    staff = get_all_staff().filter(Q(groups=get_grouptype("2")) | Q(groups=get_grouptype("1")))
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
    return render(request, 'support/listStaff.html', {"staff": se})


@group_required('type3staff')
def listStaffProposals(request, pk):
    """
    List all proposals of a staff member
    """
    user = get_all_staff().get(id=pk)

    proposals = user.proposalsresponsible.all() | user.proposals.all()
    return render(request, 'proposals/ProposalsCustomList.html',
                  {"title": "Proposals from " + user.get_full_name(), "proposals": proposals})


@group_required("type3staff")
def listStaffXls(request):
    """
    Same as supportListStaff but as XLSX
    """
    staff = get_all_staff().filter(Q(groups=get_grouptype("2")) | Q(groups=get_grouptype("1")))
    file = general_excel.listStaffXls(staff)
    response = HttpResponse(content=file)
    response['Content-Disposition'] = 'attachment; filename=marketplace-staff-list.xlsx'
    return response


@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def listStudents(request):
    """
    For support staff, supervisors and assistants to view their students.
    List all students with distributions that the current user is allowed to see.
    Including a button to view the students files.
    In later timephase shows the grades as well.

    :param request:
    :return:
    """

    if get_timephase_number() < 0:
        if get_timeslot() is None:
            raise PermissionDenied("System is closed.")
    else:
        if get_timephase_number() < 4:
            raise PermissionDenied("Students are not yet distributed")
        if get_timephase_number() < 5 and not get_grouptype("3") in request.user.groups.all():
            raise PermissionDenied(
                "When the phase 'Distribution of projects' is finished, you can view your students here.")

    cats = GradeCategory.objects.filter(TimeSlot=get_timeslot())

    des = get_distributions(request.user)
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
    return render(request, "support/listDistributedStudents.html", {"des": deslist, 'typ': cats})


@group_required('type1staff', 'type2staff', 'type3staff', 'type6staff')
def listStudentsXls(request):
    """
    Same as liststudents but as XLSX. The combination of students and grades is done in general_excel.

    :param request:
    """
    if get_timephase_number() < 4:
        raise PermissionDenied("Students are not yet distributed")
    if get_timephase_number() < 5 and not get_grouptype("3") in request.user.groups.all():
        raise PermissionDenied(
            "When the phase 'Distribution of projects' is finished, you can view your students here.")

    typ = GradeCategory.objects.filter(TimeSlot=get_timeslot())
    des = get_distributions(request.user)

    file = general_excel.listStudentsXls(des, typ)

    response = HttpResponse(content=file)
    response['Content-Disposition'] = 'attachment; filename=students-grades.xlsx'
    return response


@group_required('type3staff')
def verifyAssistants(request):
    """
    Page to let support staff give type2staffunverified the type2staff status.

    :param request:
    :return:
    """
    accounts = list(get_grouptype("2u").user_set.all())
    return render(request, "support/verifyAccounts.html", {
        "accounts": accounts
    })


@group_required('type4staff')
def listGroupProposals(request):
    """
    List all proposals of a group.
    
    :param request: 
    :return: 
    """
    obj = get_object_or_404(CapacityGroupAdministration, Members__id = request.user.id)
    props = get_all_proposals().filter(Group=obj.Group)
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals" : props,
        "title"     : "Proposals of My Group"
    })


@group_required('type3staff', 'type6staff')
def listPrivateProposals(request):
    """
    List all private proposals.
    
    :param request: 
    :return: 
    """
    props = get_all_proposals().filter(Private__isnull=False).distinct()
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals" : props,
        "title"     : "All private proposals",
        "private"   : True
    })


@group_required('type3staff')
def upgradeUser(request, pk):
    """
    Upgrade a user from type2staff to type1staff
    
    :param request: 
    :param pk: id of the user. 
    :return: 
    """
    usr = get_object_or_404(User, pk=pk)

    # verify type 2 unverified
    if get_grouptype("2u") in usr.groups.all():
        if get_grouptype("2")in usr.groups.all():
            usr.groups.remove(get_grouptype("2"))
        if get_grouptype("2u") in usr.groups.all():
            usr.groups.remove(get_grouptype("2u"))
        usr.groups.add(get_grouptype("2"))
        usr.save()
        return render(request, "base.html", {
            "Message": "Type2staff unverifed is now verified.",
            "return": "support:listusers"
        })

    if not get_grouptype("2") in usr.groups.all():
        return render(request, "base.html", {
            "Message": "Only type2staff can be upgraded.",
            "return": "support:listusers"
        })

    if get_grouptype("3") in usr.groups.all():
        return render(request, "base.html", {
            "Message": "User is supportstaff!",
            "return": "support:listusers"
        })

    if get_grouptype("1") not in usr.groups.all():
        if get_grouptype("2")in usr.groups.all():
            usr.groups.remove(get_grouptype("2"))
        if get_grouptype("2u") in usr.groups.all():
            usr.groups.remove(get_grouptype("2u"))
        usr.groups.add(get_grouptype("1"))
        usr.save()
    else:
        return render(request, "base.html", {
            "Message": "User is already upgraded!",
            "return": "support:listusers"
        })

    if cache.has_key('listusersbodyhtml'):
        cache.delete('listusersbodyhtml')
    if cache.has_key('listusersbodyhtmladmin'):
        cache.delete('listusersbodyhtmladmin')

    return render(request, "base.html", {
        "Message" : "User upgraded!",
        "return" : "support:listusers"
    })


@group_required('type3staff')
def downgradeUser(request, pk):
    """
    Change a user from type1staff to type2staff
    
    :param request: 
    :param pk: id of the staff user. 
    :return: 
    """
    usr = get_object_or_404(User, pk=pk)

    if not get_grouptype("1") in usr.groups.all():
        return render(request, "base.html", {
            "Message": "Only type1staff can be downgraded.",
            "return": "support:listusers"
        })

    if get_grouptype("3") in usr.groups.all():
        return render(request, "base.html", {
            "Message": "User is supportstaff!",
            "return": "support:listusers"
        })

    if get_grouptype("2")not in usr.groups.all() and get_grouptype("2u") not in usr.groups.all():
        if get_grouptype("1") in usr.groups.all():
            usr.groups.remove(get_grouptype("1"))
        usr.groups.add(get_grouptype("2"))
        usr.save()

    if cache.has_key('listusersbodyhtml'):
        cache.delete('listusersbodyhtml')
    if cache.has_key('listusersbodyhtmladmin'):
        cache.delete('listusersbodyhtmladmin')


    return render(request, "base.html", {
        "Message" : "User downgraded!",
        "return" : "support:listusers"
    })


#######
#Other#
#######

@group_required('type3staff')
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
        "proposalcount" : get_all_proposals().count(),
        "usercount"     : get_all_students().count() + get_all_staff().count(),
        "privatecount"  : get_all_proposals().filter(Private__isnull=False).count(),
        "groupcount"    : groupcount,
        "statuscount"   : statuscount,
        "trackcount"    : trackcount,
    })


@group_required('type3staff')
def contentpolicy(request):
    """
    List of proposal description/assignment texts that do not met the expected text.
    Example of a policy violation is an email address in a proposal description.
    
    :param request:
    """
    data = {
        "regexViolations": check_content_policy.regexTest(),
        "diffViolations": check_content_policy.diffTest(),
    }
    return render(request, "support/contentPolicyCheck.html", data)


@group_required("type3staff")
def ECTSForm(request):
    """
    Form to fill in the ECTS of students, this is done by administration staff.
    ECTS are used for the automatic distribution. ECTS changes are send using websockets to consumers.py
    
    :param request:
    """
    stds = get_all_students()
    return render(request, 'support/ECTSForm.html', {'students': stds})

##############
#Public Files#
##############

@group_required('type3staff')
def addFile(request):
    """
    Upload a public file. These files will be visible on the index page after login.    
    
    :param request: 
    :return: 
    """
    user = request.user
    if request.method == 'POST':
        form = FileAddForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            file = form.save(commit=False)
            file.User = user
            file.save()
            return render(request, "base.html",
                          {"Message": "File uploaded!", "return": "index:index"})
    else:
        form = FileAddForm(request=request)
    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Upload a public file ', 'buttontext': 'Save'})


@login_required
@group_required('type3staff')
def editFiles(request):
    """
    Edit public files. Only for supportstaff
    These files are shown on the homepage for every logged in user.
    
    :param request:
    """
    formSet = modelformset_factory(PublicFile, form=FileEditForm, can_delete=True, extra=0)
    qu = PublicFile.objects.filter(TimeSlot=get_timeslot())
    formset = formSet(queryset=qu)

    if request.method == 'POST':
        formset = formSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "File changes saved!", "return": "index:index"})
        return render(request, "base.html",
                      {"Message": "Error occurred during editing files. Possibly the file has wrong dimensions or wrong filetype.", "return": "support:editfiles"})
    else:
        return render(request, 'GenericForm.html', {'formset': formset, 'formtitle': 'All public uploaded files', 'buttontext': 'Save changes'})


#######
#Cache#
#######

@group_required('type3staff', 'type6staff')
def clearListUsersCache(request):
    """
    Clear cache for list users

    :param request:
    :return:
    """
    cache.delete('listusersbodyhtmladmin')
    cache.delete('listusersbodyhtml')

    return render(request, 'base.html', {'Message': 'Cache cleared for userlist', "return":"support:listusers"})


#
# @group_required('type3staff', 'type6staff')
# def clearCacheAllStudentsList(request):
#     """
#     Clear the cache for listStudents on OASE
#
#     :param request:
#     :return:
#     """
#     cache.delete('listallstudentsbodyhtml')
#     return render(request, 'base.html', {'Message': 'cache cleared for all students list'})
