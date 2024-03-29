#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from itertools import chain
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Sum, F
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from render_block import render_block_to_string
from datetime import datetime
from api.views import upgrade_status_api, downgrade_status_api
from distributions.utils import get_distributions
from general_mail import mail_proposal_all, mail_proposal_private
from general_model import print_list, delete_object
from general_view import get_grouptype, truncate_string
from index.decorators import group_required
from index.models import Track
from proposals import check_content_policy
from proposals.decorators import can_view_project, can_edit_project, can_share_project, can_downgrade_project, can_create_project, can_upgrade_project
from students.utils import get_all_applications
from support.models import CapacityGroup
from timeline.decorators import phase_required
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number, get_recent_timeslots
from tracking.models import ProposalTracking
from tracking.utils import tracking_visit_project
from .exports import get_list_projects_xlsx
from .forms import ProposalFormEdit, ProposalFormCreate, ProposalImageForm, ProposalDowngradeMessageForm, \
    ProposalAttachmentForm, ProposalFormLimited
from .models import Proposal, ProposalImage, ProposalAttachment
from .utils import can_edit_project_fn, prefetch, get_favorites, get_all_projects, get_share_link, get_cached_project, update_cached_project


@login_required
def list_public_projects(request, timeslot=None):
    """
    List all the public (=type4 & not-private) proposals. This is the overview for students to choose a proposal from.

    :param request:
    :return:
    """
    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
        if ts.End < datetime.now().date():  # on last day timeslot is still active
            raise PermissionDenied("Past projects cannot be browsed.")
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot

    projects = projects.filter(Q(Status=4) & Q(Private=None))
    projects = projects.select_related('ResponsibleStaff__usermeta', 'Track__Head__usermeta', 'TimeSlot', 'Group').prefetch_related('Assistants__usermeta')
    return render(request, 'proposals/list_projects.html', {
        "projects": projects,
        'timeslots': TimeSlot.objects.filter(End__gte=datetime.now()),
        'timeslot': ts,
    })


@login_required
def list_public_favorites(request, timeslot=None):
    """
    List all the public (=type4 & not-private) proposals. This is the overview for students to choose a proposal from.

    :param request:
    :return:
    """
    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
        if ts.End < datetime.now().date():  # on last day timeslot is still active
            raise PermissionDenied("Past projects cannot be browsed.")
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot

    projects = projects.filter(Q(Status=4) & Q(Private=None)).filter(favorites__User=request.user)
    projects = projects.select_related('ResponsibleStaff__usermeta', 'Track__Head__usermeta', 'TimeSlot', 'Group').prefetch_related('Assistants__usermeta')
    return render(request, 'proposals/list_projects.html', {
        'favorite': True,
        "projects": projects,
        'timeslots': TimeSlot.objects.filter(End__gte=datetime.now()),
        'timeslot': ts,
    })


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type5staff')
def list_own_projects(request, timeslot=None):
    """
    This lists all proposals that the given user has something to do with. Either a responsible or assistant. For
    Type3staff this lists all proposals. This is the usual view for staff to view their proposals.

    :param request:
    :param timeslot: optional timeslot to view proposals from, default is current ts.
    :return:
    """
    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot

    if get_grouptype("3") in request.user.groups.all() or get_grouptype("5") in request.user.groups.all():
        pass
    else:
        projects = projects.filter(Q(ResponsibleStaff=request.user) |
                                   Q(Assistants=request.user)).distinct()
    projects = prefetch(projects)
    return render(request, 'proposals/list_projects_custom.html', {
        'hide_sidebar': True,
        'projects': projects,
        'timeslots': get_recent_timeslots(),
        'timeslot': ts,
    })


@group_required('type4staff')
def list_group_projects(request, timeslot=None):
    """
    List all proposals of a group.

    :param request:
    :param timeslot: timeslot to view.l
    :return:
    """
    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot

    projects = prefetch(projects.filter(Group__Administrators=request.user).distinct())
    return render(request, 'proposals/list_projects_custom.html', {
        'hide_sidebar': True,
        'projects': projects,
        'title': 'Proposals of {}'.format(print_list(request.user.administratoredgroups.all().values_list('Group__ShortName', flat=True))),
        'timeslots': get_recent_timeslots(),
        'timeslot': ts,
    })


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type4staff')
def list_pending(request):
    """
    Get and show the pending proposals for a given user.

    :param request:
    :return:
    """
    projects = []
    if get_grouptype("2") in request.user.groups.all() or get_grouptype("2u") in request.user.groups.all():
        # type2 can only be assistant
        projects = get_all_projects().filter(Q(Assistants__id=request.user.id) & Q(Status__exact=1))

    elif get_grouptype("1") in request.user.groups.all():
        # type1 can be responsible, trackhead or assistant
        projects = get_all_projects().filter((Q(Assistants__id=request.user.id) & Q(Status__exact=1)) |
                                             (Q(ResponsibleStaff=request.user.id) & Q(Status__exact=2)) |
                                             (Q(Track__Head=request.user.id) & Q(Status__exact=3))
                                             ).distinct()
    if get_grouptype('4') in request.user.groups.all() and request.user.administratorgroups.exists():
        for group in request.user.administratorgroups.all():
            projects = set(list(chain(list(projects), list(get_all_projects().filter(Q(Group=group) & Q(Status__lte=2))))))
        title = 'Pending projects for your group'
    else:
        title = 'Pending projects'
    return render(request, "proposals/list_projects_custom.html", {
        'projects': projects,
        "title": title,
    })


@group_required('type1staff')
def list_track(request, timeslot=None):
    """
    List all proposals of the track that the user is head of.

    :param request:
    :param timeslot: Time slot to show projects from
    :return:
    """
    if not Track.objects.filter(Head=request.user).exists():
        raise PermissionDenied("This page is only for track heads.")
    tracks = Track.objects.filter(Head__id=request.user.id)

    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot
    projects = projects.filter(Track__in=tracks)
    projects = prefetch(projects)
    return render(request, "proposals/list_projects_custom.html", {
        'projects': projects,
        "title": "Proposals of track {}".format(print_list(tracks)),
        'timeslots': get_recent_timeslots(),
        'timeslot': ts,
    })


@group_required('type3staff', 'type6staff')
def list_private_projects(request, timeslot=None):
    """
    List all private proposals.

    :param request:
    :param timeslot: timeslot to show projects from.
    :return:
    """
    if timeslot:
        ts = get_object_or_404(TimeSlot, pk=timeslot)
        projects = get_all_projects(old=True).filter(TimeSlot=ts)
    else:
        ts = None
        projects = get_all_projects(old=True).filter(TimeSlot=None)  # proposals of future timeslot

    projects = prefetch(projects.filter(Private__isnull=False).distinct())
    return render(request, "proposals/list_projects_custom.html", {
        'hide_sidebar': True,
        'projects': projects,
        "title": "All private proposals",
        'timeslots': get_recent_timeslots(),
        'timeslot': ts,
        "private": True  # to show extra column with private students
    })


@can_view_project
def detail_project(request, pk):
    """
    Detailview page for a given proposal. Displays all information for the proposal. Used for students to choose a
    proposal from, and for staff to check. For staff it shows edit and up/downgrade buttons. For students it shows a
    apply or retract button.
    The proposal is cached after the create phase (phase>4). The apply/retract button is not cached but inserted using
    a .format(). Proposals are not cached for staff
    Private proposals don't have a apply/retract button, because the template doesn't have the {} in it then.

    :param request:
    :param pk: pk of the project
    :return:
    """
    proj = get_cached_project(pk)

    # if student
    if not request.user.groups.exists():
        # make apply / retract button.
        if request.user.personal_proposal.filter(TimeSlot=proj.TimeSlot).exists() or not proj.can_apply():
            button = ''
        else:
            button = '<a href="{}" class="button {}">{}</a>'
            if get_all_applications(request.user, timeslot=proj.TimeSlot).filter(Proposal=proj).exists():  # if user has applied to this proposal
                button = button.format(reverse('students:retractapplication',
                                               args=[get_all_applications(request.user, timeslot=proj.TimeSlot).filter(Proposal=proj)[0].id]),
                                       'danger',
                                       'Retract Application')
            else:  # show apply button
                button = button.format(reverse('students:confirmapply', args=[proj.id]), 'primary', 'Apply')

        # get proposal from cache, or put in cache
        cdata = cache.get("proposaldetail{}".format(pk))
        if cdata is None:
            data = {"proposal": proj,
                    "project": proj,
                    "user": request.user,
                    'cache_string_render': True
                    }
            cdata = render_block_to_string("proposals/detail_project.html", 'body', data, request=request)
            cache.set('proposaldetail{}'.format(pk), cdata, settings.PROJECT_OBJECT_CACHE_DURATION)

        tracking_visit_project(proj, request.user)  # always log visits from students

        # applications counter
        if proj.applications.exists():
            applications_count = proj.applications.count()
            applications_count_txt = '{} student'.format(applications_count)
            if applications_count > 1:
                applications_count_txt += 's'
        else:
            applications_count_txt = 'No one applied to this project yet.'

        return render(request, "proposals/detail_project.html", {
            "bodyhtml": cdata.format(apply_buttons=button, applications_counter=applications_count_txt),
            'project': proj,
        })  # send project for if statement in scripts.

    # if staff:
    else:
        data = {"proposal": proj,
                "project": proj,
                "Editlock": "Editing not possible"}
        if proj.Status == 4:
            # support staff can see applications and distributions always
            if get_grouptype("3") in request.user.groups.all():
                data['applications'] = proj.applications.all()
                data['distributions'] = get_distributions(request.user, timeslot=proj.TimeSlot).filter(Proposal=proj)
            # other staff users can see old distributions and current in phase 4+
            elif (get_grouptype('2u') not in request.user.groups.all()) and \
                    proj.prevyear() or (proj.curyear() and get_timephase_number() >= 4):
                data['distributions'] = get_distributions(request.user, timeslot=proj.TimeSlot).filter(Proposal=proj)

        allowed = can_edit_project_fn(request.user, proj, False)
        if allowed[0]:
            data['Editlock'] = False
        else:
            data['Editlock'] = allowed[1]
        data['cpv'] = cache.get('cpv_proj_{}'.format(proj.id))  # if cpv is not in cache, ignore
        return render(request, "proposals/detail_project.html", data)


@can_create_project
def create_project(request):
    """
    Create a new proposal. Only for staff. Generating a new proposal for this timeslot is only allowed in the first
    timephase. In other timephases projects can only be generated for the next timeslot.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ProposalFormCreate(request.POST, request=request)
        if form.is_valid():
            prop = form.save()
            mail_proposal_all(request, prop)
            check_content_policy.CPVCheckThread(prop).start()
            if prop.Private.all():
                for std in prop.Private.all():
                    mail_proposal_private(prop, std, "A private proposal was created for you.")
            return render(request, "proposals/message_project.html", {"Message": "Proposal created!", "project": prop})
    else:
        init = {}
        if get_grouptype("1") in request.user.groups.all():
            init["ResponsibleStaff"] = request.user.id
        elif get_grouptype("2") in request.user.groups.all() or get_grouptype('2u'):
            init["Assistants"] = [request.user.id]
        form = ProposalFormCreate(request=request, initial=init)
    if get_timephase_number() == 1:
        return render(request, 'GenericForm.html', {'form': form,
                                                    'formtitle': 'Create new Proposal',
                                                    'buttontext': 'Create and go to next step'})
    else:
        return render(request, 'GenericForm.html', {'form': form,
                                                    'formtitle': 'Create new Proposal (For next timeslot)',
                                                    'buttontext': 'Create and go to next step'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_edit_project
def edit_project(request, pk):
    """
    Edit a given proposal. Only for staff that is allowed to edit the proposal. Time slot validation is handled in form.

    :param request:
    :param pk: pk of the proposal to edit.
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    title = 'Edit Proposal'
    template = 'GenericForm.html'

    if request.method == 'POST':
        # only limited editing when status 4
        if obj.Status == 4:
            form = ProposalFormLimited(request.POST, request=request, instance=obj)
        else:
            form = ProposalFormEdit(request.POST, request.FILES, request=request, instance=obj)
        if form.is_valid():
            obj = form.save()
            if form.changed_data:
                update_cached_project(obj)
                check_content_policy.CPVCheckThread(obj).start()
                if obj.Private.all():
                    for std in obj.Private.all():
                        mail_proposal_private(obj, std, "Your private proposal was edited.")
            return render(request, "proposals/message_project.html", {"Message": "Proposal saved!", "project": obj})
    else:
        if obj.Status == 4:
            form = ProposalFormLimited(request=request, instance=obj)
            title = 'Edit active Proposal'
            template = 'proposals/form_active_proposal.html'
        else:
            form = ProposalFormEdit(request=request, instance=obj)
    return render(request, template, {'form': form, 'formtitle': title, 'buttontext': 'Save'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_view_project
def copy_project(request, pk):
    """
    Copy a proposal from a previous timeslot. Only for staff that is allowed to see the proposal to copy.

    :param pk: the id of proposal to copy
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = ProposalFormCreate(request.POST, request=request)
        if form.is_valid():
            prop = form.save()

            mail_proposal_all(request, prop)
            if prop.Private.all():
                for std in prop.Private.all():
                    mail_proposal_private(prop, std, "A private proposal was created for you.")
            return render(request, "proposals/message_project.html", {"Message": "Proposal created!", "project": prop})
    else:
        old_proposal = get_object_or_404(Proposal, pk=pk)
        oldpk = old_proposal.pk
        old_proposal.pk = None
        # default timeslot. Overridden by form if this is not in phase 1.
        old_proposal.TimeSlot = get_timeslot()
        # Assistants and privates are removed, because m2m is not copied in this way.
        form = ProposalFormCreate(request=request, instance=old_proposal, copy=oldpk)
    return render(request, 'GenericForm.html', {'form': form,
                                                'formtitle': 'Edit copied proposal',
                                                'buttontext': 'Create and go to next step'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_edit_project
def add_file(request, pk, ty):
    """
    Add a file of type ty to a project. The type can be an image or a file (usually pdf). The image is shown in an
    image slider, an attachment is shown as a download button.

    :param request:
    :param pk: pk of the project
    :param ty: type of file to add. i for image, a for attachment
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if ty == "i":
        ty = "image"
        form = ProposalImageForm
    elif ty == "a":
        ty = "attachment"
        form = ProposalAttachmentForm
    else:
        raise PermissionDenied("Invalid type supplied")

    if request.method == 'POST':
        form = form(request.POST, request.FILES, request=request)
        if form.is_valid():
            file = form.save(commit=False)
            file.Proposal = obj
            file.save()
            return render(request, "proposals/message_project.html",
                          {"Message": "File to Proposal saved! Click the button below to add another file.",
                           "project": obj})

    return render(request, 'GenericForm.html',
                  {'form': form, 'formtitle': 'Add ' + ty + ' to project ' + obj.Title, 'buttontext': 'Save'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_edit_project
def edit_file(request, pk, ty):
    """
    Edit a file of a project.

    :param request:
    :param pk: pk of the proposal to edit file of
    :param ty: type of file to edit, either i for image or a for attachement
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if ty == "i":
        ty = "image"
        model = ProposalImage
        form = ProposalImageForm
    elif ty == "a":
        ty = "attachment"
        model = ProposalAttachment
        form = ProposalAttachmentForm
    else:
        raise PermissionDenied("Invalid type supplied")

    form_set = modelformset_factory(model, form=form, can_delete=True, extra=0)
    qu = model.objects.filter(Proposal=obj)

    formset = form_set(queryset=qu)

    if request.method == 'POST':
        formset = form_set(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render(request, "proposals/message_project.html",
                          {"Message": "File changes saved!", "project": obj})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': 'All ' + ty + 's in project ' + obj.Title, "Proposal": obj.pk,
                   'buttontext': 'Save changes'})


@group_required('type3staff')
def ask_delete_project(request, pk):
    """
    A confirmform for type3staff to delete a proposal. Regular staff cannot delete a proposal, as this should not
    happen. Public (=status4) proposals cannot be deleted.
    :param request:
    :param pk: pk of proposal to delete.
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if obj.Status >= 3:
        return render(request, "proposals/message_project.html",
                      {"Message": "This Proposal is already approved or public, it cannot be deleted", "project": obj},
                      status=403)
    form = "<a href=" + reverse('proposals:deleteproposal', kwargs={"pk": int(
        pk)}) + " class='button warning'><span class='mif-bin'></span>click here to DELETE</a></button></form>"
    return render(request, "base.html",
                  {"Message": "Are you sure to delete? This cannot be undone " + form})


@group_required('type3staff')
def delete_project(request, pk):
    """
    Really delete a proposal. This can only be called by type3staff after going to the confirm delete page.

    :param request:
    :param pk: pk of the proposal to delete
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if obj.Status >= 3:
        return render(request, "proposals/message_project.html",
                      {"Message": "Proposal is locked for editing", "project": obj},
                      status=403)

    if "HTTP_REFERER" in request.META:
        if 'ask' in request.META['HTTP_REFERER']:
            # make sure previous page is askdelete
            title = obj.Title
            delete_object(obj)
            return render(request, "base.html",
                          {"Message": "Proposal " + title + " is removed", "return": ""})
    raise PermissionDenied("You should not access this page directly")


@can_upgrade_project
def upgrade_status(request, pk):
    """
    Upgrade the status of a given proposal.

    :param request:
    :param pk: pk of the proposal to upgrade
    :return:
    """
    r = upgrade_status_api(request, pk)
    obj = get_object_or_404(Proposal, pk=pk)  # should be after upgrade
    return render(request, "proposals/message_project.html", {"Message": r.content.decode(), "project": obj},
                  status=r.status_code)


@can_downgrade_project
def downgrade_status(request, pk):
    """
    Downgrade the status of a proposal, and send the affected users (responsible and assistants) a mail that their
    proposal is downgraded in status. Mailing is done via mailaffecteduser via downgradestatusApi.

    :param request:
    :param pk: pk of the proposal to downgrade
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if request.user == obj.ResponsibleStaff or request.user == obj.Track.Head:
        if request.method == "POST":
            form = ProposalDowngradeMessageForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['Message']
                r = downgrade_status_api(request, pk, message)
                obj = get_object_or_404(Proposal, pk=pk)  # should be after downgrade
                notify = r.content.decode()
                if message != '':
                    notify += "<br />With note: <br /> {}".format(message)
                return render(request, "proposals/message_project.html", {"Message": notify, "project": obj},
                              status=r.status_code)
        else:
            form = ProposalDowngradeMessageForm()  # request=request
            return render(request, 'GenericForm.html',
                          {'form': form, 'formtitle': 'Message for downgrade proposal ' + obj.Title,
                           'buttontext': 'Downgrade and send message'})
    else:  # assistant downgrade does not get the message field.
        r = downgrade_status_api(request, pk)
        obj = get_object_or_404(Proposal, pk=pk)  # should be after downgrade
        return render(request, "proposals/message_project.html", {"Message": r.content.decode(), "project": obj},
                      status=r.status_code)


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_share_project
def share(request, pk):
    """
    Get a sharelink for a given proposal. This link is a public view link for a proposal-detailpage for when the
    proposal is not yet public.

    :param request:
    :param pk: Proposal pk to get sharelink for
    :return:
    """
    link = get_share_link(pk)
    return render(request, "base.html", {
        "Message": "Share link created: <a href=\"{}\">{}</a> <br/>"
                   " Use this to show the proposal to anybody without an account. "
                   "The link will be valid for seven days.".format(link, link),
    })


def view_share_link(request, token):
    """
    Translate a given sharelink to a proposal-detailpage.

    :param request:
    :param token: sharelink token, which includes the pk of the proposal
    :return: proposal detail render
    """
    try:
        pk = signing.loads(token, max_age=settings.MAXAGESHARELINK)
    except signing.SignatureExpired:
        return render(request, "base.html", {
            "Message": "Share link has expired!"
        })
    except signing.BadSignature:
        return render(request, "base.html", {
            "Message": "Invalid token in share link!"
        })
    obj = get_object_or_404(Proposal, pk=pk)
    return render(request, "proposals/detail_project.html", {
        "proposal": obj,
        "project": obj
    })


@group_required('type1staff', 'type2staff', 'type3staff', 'type4staff')
@phase_required(5, 6, 7)
def stats_personal(request, timeslot, step=0):
    """
    Gives an overview of the statistics of the proposals of the user.
    These include the amount of visitors and applications.
    This is only for timephase 5 and later

    :param request:
    :param step: integer, which step of the wizard view you want to see, supplied via URI
    :return:
    """
    timeslot = get_object_or_404(TimeSlot, pk=timeslot)
    step = int(step)
    projects = get_all_projects(old=True).filter(TimeSlot=timeslot, Status=4)
    if get_grouptype("3") in request.user.groups.all():
        pass
    else:
        projects = projects.filter(Q(ResponsibleStaff=request.user) |
                                   Q(Assistants=request.user) |
                                   Q(Group__Administrators=request.user))
    projects = list(projects.distinct().annotate(Count('distributions')).order_by('-distributions__count'))
    if step == 0:
        return render(request, "proposals/stats_project_personal.html", {"step": 0, 'timeslot': timeslot, 'timeslots': TimeSlot.objects.exclude(pk=timeslot.pk)})
    elif step == 1:
        counts = []
        tabledata = []
        for p in projects:
            try:
                counts.append(p.tracking.UniqueVisitors.count())
            except ProposalTracking.DoesNotExist:
                counts.append(0)
            try:
                tabledata.append({
                    "prop": p,
                    "count": p.tracking.UniqueVisitors.count()
                })
            except ProposalTracking.DoesNotExist:
                tabledata.append({
                    "prop": p,
                    "count": 0
                })
        return render(request, "proposals/stats_project_personal.html", {
            "counts": counts,
            "labels": [truncate_string(p.Title) for p in projects],
            "tabledata": tabledata,
            "step": 1,
            'timeslot': timeslot,
        })
    else:
        if step - 2 >= len(projects):
            return render(request, "proposals/stats_project_personal.html", {"step": -1, 'timeslot': timeslot})
        prop = projects[step - 2]
        try:
            count = prop.tracking.UniqueVisitors.count()
        except ProposalTracking.DoesNotExist:
            count = 0

        return render(request, "proposals/stats_project_personal.html", {
            "prop": prop,
            "visitors": count,
            "applications": [prop.applications.filter(Priority=n).count() for n in range(1, settings.MAX_NUM_APPLICATIONS + 1)],
            "distributed": prop.distributions.count(),
            "step": step,
            'timeslot': timeslot
        })


@group_required('type1staff', 'type2staff', 'type3staff', 'type4staff', 'type5staff', 'type6staff')
def project_stats(request, timeslot=None):
    """
    Statistics for projects, allowed for all staff except unverified.

    :param request:
    :param timeslot: the time slot to view proposals from
    :return:
    """
    Project = Proposal
    if timeslot is None:
        # all projects
        p = Proposal.objects.filter(TimeSlot=None)
    else:
        timeslot = get_object_or_404(TimeSlot, pk=timeslot)
        p = Proposal.objects.filter(TimeSlot=timeslot)

    totalnum = p.count()

    groups = CapacityGroup.objects.all()
    group_count_prop = []
    group_count2_prop = []
    group_count_distr = []
    group_count_appl = []
    group_labels = []
    group_labels_appl = []
    group_labels_distr = []
    group_labels_prop = []

    for group in groups:  # groups is tupple of (shortname, longname)
        group_labels.append(str(group))
        group_count_prop.append(p.filter(Group=group).count())
        group_count2_prop.append(p.filter(Group=group).aggregate(Sum('NumStudentsMax'))['NumStudentsMax__sum'] or 0)
        group_count_distr.append(p.filter(Group=group, distributions__isnull=False).count())  # not distinct because users.
        group_count_appl.append(p.filter(Group=group, applications__isnull=False).count())  # not distinct because users.

    # sort both lists for each count-type by count number, make sure labels are in correct order.
    if group_count_prop:
        group_count_prop, group_count2_prop, group_labels_prop = (list(t) for t in
                                                                  zip(*sorted(zip(group_count_prop, group_count2_prop, group_labels), reverse=True)))
    if group_count_distr:
        group_count_distr, group_labels_distr = (list(t) for t in
                                                 zip(*sorted(zip(group_count_distr, group_labels), reverse=True)))
    if group_count_appl:
        group_count_appl, group_labels_appl = (list(t) for t in
                                               zip(*sorted(zip(group_count_appl, group_labels), reverse=True)))
    status_count = []
    status_labels = []
    for option in Project.StatusOptions:
        status_count.append(p.filter(Status=option[0]).count())
        status_labels.append(option[1])
    if status_count:
        status_count, status_labels = (list(t) for t in zip(*sorted(zip(status_count, status_labels), reverse=True)))

    track_count = []  # n projects
    track_count2 = []  # max capacity
    track_labels = []
    for track in Track.objects.all():
        track_count.append(p.filter(Track=track).distinct().count())
        track_count2.append(p.filter(Track=track).distinct().aggregate(Sum('NumStudentsMax'))['NumStudentsMax__sum'] or 0)
        track_labels.append(track.__str__())
    if track_count:
        track_count, track_count2, track_labels = (list(t) for t in zip(*sorted(zip(track_count, track_count2, track_labels), reverse=True)))

    return render(request, 'proposals/stats_project.html', {
        'num': totalnum,
        # 'done': p.filter(Approved=True).count(),
        'timeslots': get_recent_timeslots(),
        'timeslot': timeslot,
        "mincapacity": p.aggregate(Sum('NumStudentsMin'))['NumStudentsMin__sum'],
        "maxcapacity": p.aggregate(Sum('NumStudentsMax'))['NumStudentsMax__sum'],
        'data': [
            {
                'label': 'Projects by capacity group',
                'labels': group_labels_prop,
                'count_label2': 'Max cap.',
                'counts': group_count_prop,
                'counts2': group_count2_prop,
                'total': sum(group_count_prop),
                'total2': sum(group_count2_prop),
            }, {
                #     'label': 'Master program',
                #     'labels': program_labels,
                #     'counts': program_count,
                #     'total': totalnum,
                # }, {
                'label': 'Status options',
                'labels': status_labels,
                'counts': status_count,
                'total': sum(status_count),
            }, {
                'label': 'Track options',
                'labels': track_labels,
                'count_label2': 'Max cap.',
                'counts': track_count,
                'counts2': track_count2,
                'total': sum(track_count),
                'total2': sum(track_count2),
            }, {
                'label': 'Applications by capacity group',
                'labels': group_labels_appl,
                'counts': group_count_appl,
                'total': sum(group_count_appl),
            }, {
                'label': 'Distributions by capacity group',
                'labels': group_labels_distr,
                'counts': group_count_distr,
                'total': sum(group_count_distr),
            },
            # {
            #     'label': 'Progress',
            #     'labels': progress_labels,
            #     'counts': progress_count,
            #     'total': sum(progress_count),
            # }, {
            #     'label': 'Type',
            #     'labels': type_labels,
            #     'counts': type_count,
            #     'total': sum(type_count),
            # }
        ],
    })


@group_required('type3staff')
def content_policy_calc(request):
    """
    List of proposal description/assignment texts that do not met the expected text.
    Example of a policy violation is an email address in a proposal description.

    :param request:
    """
    projects = get_all_projects(old=False)
    check_content_policy.CPVCheckThread(projects).start()
    return render(request, "proposals/cpv_progress.html")


@group_required('type3staff')
def content_policy_view(request):
    results = []
    for pk in get_all_projects(old=False).values_list('pk', flat=True):
        c = cache.get('cpv_proj_{}'.format(pk))
        if c:
            results.append(c)
    return render(request, 'proposals/content_policy_violations.html', {
        'pattern_policies': check_content_policy.content_policies,
        'length_requirements': check_content_policy.length_requirements.items(),
        'results': results,
    })


@group_required('type3staff')
def exports(request, download=None):
    ts = get_timeslot()
    if ts is None:
        # timeslot already finished, get last active timeslot.
        ts = TimeSlot.objects.order_by('End').last()
    if not download:
        return render(request, 'proposals/exports.html', context = {'timeslot':ts})
    else:
        if download == 'published':
            projects = Proposal.objects.filter(TimeSlot=ts, Status=4).order_by('Title')
        elif download == 'all':
            projects = Proposal.objects.filter(TimeSlot=ts).order_by('Title')
        elif download == 'nonfull':
            projects = Proposal.objects.annotate(num_distr=Count('distributions')).filter(TimeSlot=ts, Status=4, num_distr__lt=F(
                'NumStudentsMax')).order_by('Title')
        elif download == 'nondistributed':
            projects = Proposal.objects.filter(TimeSlot=ts, Status=4, distributions__isnull=True).order_by('Title')
        else:
            raise PermissionDenied('Invalid download.')
    wb = get_list_projects_xlsx(projects)
    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        response = HttpResponse(content=tmp.read())
        response['Content-Disposition'] = f'attachment; filename=export-proposals-{download}.xlsx'
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response
