#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from index.decorators import group_required
from proposals.decorators import can_edit_project, can_downgrade_project
from api.utils import get_status_str
from general_mail import mail_proposal_all, send_mail
from general_view import get_grouptype
from proposals.models import Proposal
from proposals.utils import get_all_proposals
from support.models import GroupAdministratorThrough, CapacityGroup
from timeline.utils import get_timeslot, get_timephase_number
from tracking.models import ProposalStatusChange


@login_required
def api_info(request):
    return render(request, 'api/api.html')


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_edit_project
def upgrade_status_api(request, pk):
    """
    API call to increase the status of a proposal.

    :param request:
    :param pk: id of proposal
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)

    if obj.Status == 4:
        return HttpResponse("Already at final stage", status=403)

    if obj.Status == 3 and obj.nextyear():
        return HttpResponse("Cannot publish proposal for future timeslot", status=403)

    elif get_timephase_number() > 2 and \
            obj.TimeSlot == get_timeslot() and \
            get_grouptype('3') not in request.user.groups.all():
        return HttpResponse("Proposal frozen in this timeslot. The timephase of editing has ended.", status=403)

    elif request.user in obj.Assistants.all() and obj.Status >= 2:
        return HttpResponse("You are an assistant and not allowed to increase status further", status=403)
    # Done in can_edit decorator
    # elif obj.Track.Head != request.user and obj.Status > 2 and not get_grouptype('3') in request.user.groups.all():
    #     return HttpResponse("Not allowed to publish as non track head", status=403)

    else:
        oldstatus = obj.Status
        if oldstatus == 2:
            # per default go to publish from 4, 3 is only used if it is explicitly downgraded
            newstatus = 4
        else:
            newstatus = obj.Status + 1

        obj.Status = newstatus
        obj.save()
        mail_proposal_all(request, obj)

        notification = ProposalStatusChange()
        notification.Subject = obj
        notification.Actor = request.user
        notification.StatusFrom = oldstatus
        notification.StatusTo = newstatus
        notification.save()

        if obj.Status > 3:
            for assistant in obj.Assistants.all():
                if get_grouptype("2u") in assistant.groups.all():
                    verify_assistant_fn(assistant)
        if obj.Status == 4:
            # put the object in cache if status goes from 3->4
            cache.set('proposal_{}'.format(pk), obj, None)
            cache.delete('listproposalsbodyhtml')
        return HttpResponse(get_status_str(obj.Status))


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff', 'type4staff')
@can_downgrade_project
def downgrade_status_api(request, pk, message=''):
    """
    API call to decrease the status of a proposal.

    :param request:
    :param pk: id of proposal
    :param message: message why the proposal was downgraded
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    oldstatus = obj.Status

    if oldstatus == 4:
        # track head downgrade to 3, owner downgrade to 4
        if request.user == obj.Track.Head:
            newstatus = 3
        else:
            newstatus = 2
    else:
        newstatus = oldstatus - 1

    obj.Status = newstatus
    obj.save()
    mail_proposal_all(request, obj, message)

    notification = ProposalStatusChange()
    notification.Subject = obj
    notification.Message = message
    notification.Actor = request.user
    notification.StatusFrom = oldstatus
    notification.StatusTo = newstatus
    notification.save()

    # destroy the cache for this if oldstatus was published
    if oldstatus == 4:
        if 'listproposalsbodyhtml' in cache:
            cache.delete('listproposalsbodyhtml')
        if 'proposal_{}'.format(pk) in cache:
            cache.delete('proposal_{}'.format(pk))
        if 'proposaldetail{}'.format(pk) in cache:
            cache.delete('proposaldetail{}'.format(pk))

    return HttpResponse(get_status_str(obj.Status))


@group_required('type3staff')
def verify_assistant(request, pk):
    """
    API call to verify an type2staffunverified assistant as a type2staff.

    :param request:
    :param pk: id of the assistant-user
    :return:
    """
    account = get_object_or_404(User, pk=pk)

    if get_grouptype("2u") not in account.groups.all():
        return HttpResponse("This account is already verified")

    if verify_assistant_fn(account):
        return HttpResponse("Account verified!")
    else:
        return HttpResponse("Verify failed!")


def verify_assistant_fn(user):
    """
    Verify an unverified user and mail a confirmation.

    :param user:
    :return:
    """
    account_group = User.groups.through.objects.get(user=user)
    account_group.group = get_grouptype("2")
    account_group.save()
    # inform the user of verification.
    send_mail("user groups changed", "email/user_groups_changed.html",
              {'oldgroups': 'type2staff unverified',
               'newgroups': 'type2staff',
               'message': 'Your account is now verified!',
               'user': user},
              user.email)
    return True


@login_required
def list_public_projects_api(request):
    """
    Return all public proposals (=type 4) ordered by group as JSON

    :param request:
    :return: JSON response
    """
    data = {}

    for group in CapacityGroup.objects.all():
        data[group.ShortName] = {
            "name": group.ShortName,
            "projects": [prop.id for prop in
                         get_all_proposals().filter(Q(Status=4) & Q(Group=group) & Q(Private__isnull=True))]
        }

    return JsonResponse(data)


@login_required
def list_public_projects_titles_api(request):
    """
    Get all public proposals (=status 4) titles as JSON

    :param request:
    :return: JSON response
    """
    data = {}

    for prop in get_all_proposals().filter(Q(Status=4) & Q(Private__isnull=True)):
        data[prop.id] = prop.Title

    return JsonResponse(data)


@login_required
def detail_proposal_api(request, pk):
    """
    Get detailed information of given proposal as JSON

    :param request:
    :param pk: id of the proposal
    :return:
    """
    prop = get_object_or_404(Proposal, pk=pk)
    if prop.Status != 4 or prop.Private.exists():
        return HttpResponse("Not allowed", status=403)
    return JsonResponse({
        "id": prop.id,
        "detaillink": reverse("proposals:details", kwargs={'pk': prop.id}),
        "title": prop.Title,
        "group": prop.Group.ShortName,
        "track": str(prop.Track),
        "reponsible": str(prop.ResponsibleStaff),
        "assistants": [str(u) for u in list(prop.Assistants.all())],
        "generaldescription": prop.GeneralDescription,
        "taskdescription": prop.StudentsTaskDescription,
    })


@login_required
def list_published_api(request):
    """
    JSON list of all published proposals with some detail info.

    :param request:
    :return:
    """
    props = get_all_proposals().filter(Q(Status=4) & Q(Private__isnull=True))
    prop_list = []
    for prop in props:
        prop_list.append({
            "id": prop.id,
            "detaillink": reverse("proposals:details", args=[prop.id]),
            "title": prop.Title,
            "group": prop.Group.ShortName,
            "track": str(prop.Track),
            "reponsible": str(prop.ResponsibleStaff),
            "assistants": [str(u) for u in list(prop.Assistants.all())],
        })
    return JsonResponse(prop_list, safe=False)


@group_required('type3staff')
def get_group_admins(request, pk, type):
    group = get_object_or_404(CapacityGroup, pk=pk)
    if type == 'read':
        return JsonResponse([g.User.id for g in GroupAdministratorThrough.objects.filter(Group=group, Super=False)],
                            safe=False)
    elif type == 'write':
        return JsonResponse([g.User.id for g in GroupAdministratorThrough.objects.filter(Group=group, Super=True)],
                            safe=False)
    else:
        return HttpResponseBadRequest()
