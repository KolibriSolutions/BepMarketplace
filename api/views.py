from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from BepMarketplace.decorators import group_required, can_edit_proposal, superuser_required, can_downgrade_proposal
from api.utils import getStatStr
from general_mail import mailAffectedUser
from general_model import GroupOptions
from general_view import get_grouptype
from proposals.models import Proposal
from proposals.utils import get_all_proposals
from support.models import CapacityGroupAdministration
from timeline.utils import get_timeslot, get_timephase_number
from tracking.models import ProposalStatusChange

@login_required
def api_info(request):
    return render(request, 'api/api.html')


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_edit_proposal
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
        return HttpResponse("Proposal frozen in this timeslot", status=403)

    elif request.user in obj.Assistants.all() and obj.Status >= 2:
        return HttpResponse("You are an assistant and not allowed to increase status further", status=403)
    # Done in can_edit decorator
    # elif obj.Track.Head != request.user and obj.Status > 2 and not get_grouptype('3') in request.user.groups.all():
    #     return HttpResponse("Not allowed to publish as non track head", status=403)

    else:

        obj.Status += 1
        obj.save()
        mailAffectedUser(request, obj)

        notification = ProposalStatusChange()
        notification.Subject = obj
        notification.Actor = request.user
        notification.StatusFrom = obj.Status - 1
        notification.StatusTo = obj.Status
        notification.save()

        if obj.Status == 3:
            for assistant in obj.Assistants.all():
                if get_grouptype("2u") in assistant.groups.all():
                    account_group = User.groups.through.objects.get(user=assistant)
                    account_group.group = get_grouptype("2")
                    account_group.save()
        # put the object in cache if status goes from 3->4
        if obj.Status == 4:
            cache.set('proposal_{}'.format(pk), obj, None)
            cache.delete('listproposalsbodyhtml')
        return HttpResponse(getStatStr(obj.Status))


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_downgrade_proposal
def downgrade_status_api(request, pk, message=''):
    """
    API call to decrease the status of a proposal.

    :param request:
    :param pk: id of proposal
    :param message: message why the proposal was downgraded
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    # Status 2 always allowed
    # Status 3: (timephase 1 responsible+trackhead) (timephase 2 only trackhead)
    # Status 4: trackhead
    obj.Status -= 1
    obj.save()
    mailAffectedUser(request, obj, message)

    notification = ProposalStatusChange()
    notification.Subject = obj
    notification.Message = message
    notification.Actor = request.user
    notification.StatusFrom = obj.Status + 1
    notification.StatusTo = obj.Status
    notification.save()

    # destroy the cache for this if the status went from 4->3
    if obj.Status == 3:
        if cache.has_key('listproposalsbodyhtml'):
            cache.delete('listproposalsbodyhtml')
        if cache.has_key('proposal_{}'.format(pk)):
            cache.delete('proposal_{}'.format(pk))
        if cache.has_key('proposaldetail{}'.format(pk)):
            cache.delete('proposaldetail{}'.format(pk))

    return HttpResponse(getStatStr(obj.Status))


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

    account_group = User.groups.through.objects.get(user=account)
    account_group.group = get_grouptype("2")
    account_group.save()

    return HttpResponse("Account verified!")


@superuser_required()
def get_group_admins(request, group=""):
    """
    Get all capacity group administration members as JSON

    :param request:
    :param group: the group where you want the administration member from
    :return:
    """
    objs = CapacityGroupAdministration.objects.filter(Group=group)
    if not objs.exists():
        return HttpResponse("Could not find group")
    else:
        obj = objs[0]

    mmbrs = set()
    for m in obj.Members.all():
        mmbrs.add(str(m.id))
    return JsonResponse(list(mmbrs), safe=False)


@login_required
def list_public_projects_api(request):
    """
    Return all public proposals (=type 4) ordered by group as JSON

    :param request:
    :return: JSON response
    """
    data = {}

    for group in GroupOptions:
        data[group[0]] = {
            "name": group[0],
            "projects": [prop.id for prop in
                         get_all_proposals().filter(Q(Status=4) & Q(Group=group[0]) & Q(Private__isnull=True))]
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
        "group": prop.Group,
        "track": str(prop.Track),
        "ECTS": prop.ECTS,
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
    l = []
    for prop in props:
        l.append({
            "id": prop.id,
            "detaillink": reverse("proposals:details", args=[prop.id]),
            "title": prop.Title,
            "group": prop.Group,
            "track": str(prop.Track),
            "ECTS": prop.ECTS,
            "reponsible": str(prop.ResponsibleStaff),
            "assistants": [str(u) for u in list(prop.Assistants.all())],
        })
    return JsonResponse(l, safe=False)
