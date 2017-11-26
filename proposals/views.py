from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from render_block import render_block_to_string

from BepMarketplace.decorators import group_required, can_edit_proposal, can_view_proposal, can_downgrade_proposal
from api.views import upgradeStatusApi, downgradeStatusApi
from general_mail import mailAffectedUser, mailPrivateStudent
from general_model import GroupOptions
from general_view import createShareLink, get_timephase_number, get_distributions, get_all_proposals, get_grouptype, \
    get_timeslot
from index.models import Track
from tracking.views import trackProposalVisit
from .cacheprop import getProp, updatePropCache
from .forms import ProposalFormEdit, ProposalFormCreate, ProposalImageForm, ProposalDowngradeMessageForm, \
    ProposalAttachmentForm
from .models import Proposal, ProposalImage, ProposalAttachment


@login_required
def listProposals(request):
    """
    List all the public (=type4 & not-private) proposals. This is the overview for students to choose a proposal from.

    :param request:
    :return:
    """

    bodyhtml = cache.get('listproposalsbodyhtml')
    if bodyhtml is None:
        proposals = get_all_proposals().filter(Q(Status=4) & Q(Private=None))
        bodyhtml = render_block_to_string("proposals/ProposalList.html", 'body', {"proposals":proposals})
        cache.set('listproposalsbodyhtml', bodyhtml, None)
    return render(request, 'proposals/ProposalList.html', {"bodyhtml" : bodyhtml})


@can_view_proposal
def detailProposal(request, pk):
    """
    Detailview page for a given proposal. Displays all information for the proposal. Used for students to choose a
    proposal from, and for staff to check. For staff it shows edit and up/downgrade buttons. For students it shows a
    apply or retract button.
    The proposal is cached after the create phase (phase>4). The apply/retract button is not cached but inserted using
    a .format(). Proposals are not cached for staff
    Private proposals don't have a apply/retract button, because the template doesn't have the {} in it then.

    :param request:
    :param pk: pk of the proposal
    :return:
    """
    prop = getProp(pk)

    # if student
    if not request.user.groups.exists():
        # make apply / retract button.
        if get_timephase_number() != 3:  # phase 3 is for students choosing projects.
            button = ''
        else:
            button = '<a href="{}" class="button {}">{}</a>'
            if request.user.applications.filter(Proposal=prop).exists():  # if user has applied to this proposal
                button = button.format(reverse('students:retractapplication',
                                               args=[request.user.applications.filter(Proposal=prop)[0].id]), 'danger',
                                       'Retract Application')
            else:  # show apply button
                button = button.format(reverse('students:confirmapply', args=[prop.id]), 'primary', 'Apply')

        # get proposal from cache, or put in cache
        cdata = cache.get("proposaldetail{}".format(pk))
        if cdata is None:
            data = {"proposal": prop,
                    "user": request.user
                    }
            cdata = render_block_to_string("proposals/ProposalDetail.html", 'body', data)
            cache.set('proposaldetail{}'.format(pk), cdata, None)

        trackProposalVisit(prop, request.user)  # always log visits from students
        return render(request, "proposals/ProposalDetail.html", {"bodyhtml": cdata.format(button)})

    # if staff:
    else:
        data = {"proposal": prop}
        data["Editlock"] = "Editing not possible"
        if prop.Status == 4:  # published proposal in this timeslot
            if not prop.prevyear() and (request.user in prop.Assistants.all()
                                 or prop.ResponsibleStaff == request.user):
                data["Editlock"] =\
                    "To edit, first downgrade the proposal or ask your track head (" + prop.Track.Head.get_full_name() + ") to do so."
            if get_grouptype("3") in request.user.groups.all() and get_timephase_number() > 2:  # support staff can see applications
                data['applications'] = prop.applications.all()
            if get_timephase_number() >= 4:  # responsible / assistants can see distributions in distribution phase
                data['distributions'] = get_distributions(request.user).filter(Proposal=prop)
        elif not prop.prevyear():  # not published proposal, status 1, 2, and 3 and from this timeslot
            # support staf or superusers are always allowed to edit, in any timephase as long as proposal is not published
            if get_grouptype("3") in request.user.groups.all():
                data["Editlock"] = False
            # in the create and check phase
            elif get_timephase_number() < 3:
                # track heads are allowed to edit
                if prop.Track.Head == request.user:
                    data["Editlock"] = False
                # if status is either 1 or 2 and user is assistant edit is allowed
                elif request.user in prop.Assistants.all() or prop.ResponsibleStaff == request.user:
                    if prop.Status == 3:
                        if get_timephase_number() == 2:
                            data["Editlock"] = "To edit, first downgrade the proposal or ask your track head ("+prop.Track.Head.get_full_name()+") to do so."
                        else:  # in timephase 1 the responsible can also downgrade.
                            data["Editlock"] = "To edit, first downgrade the proposal or ask the responsible staff or track head (" + prop.Track.Head.get_full_name() + ") to do so."
                    else:  # editing allowed in status 1 and 2
                        data["Editlock"] = False
        return render(request, "proposals/ProposalDetail.html", data)


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
def createProposal(request):
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
            mailAffectedUser(request, prop)
            if prop.Private.all():
                for std in prop.Private.all():
                    mailPrivateStudent(request, prop, std, "A private proposal was created for you.")
            return render(request, "proposals/ProposalMessage.html", {"Message": "Proposal created!", "Proposal": prop})
    else:
        init = {'ECTS': "15"}
        if get_grouptype("1") in request.user.groups.all():
            init["ResponsibleStaff"] = request.user.id
        elif get_grouptype("2") in request.user.groups.all() or get_grouptype('2u'):
            init["Assistants"] = [request.user.id]
        form = ProposalFormCreate(request=request,initial=init)
    if get_timephase_number() == 1:
        return render(request, 'GenericForm.html', {'form':form,
                                                'formtitle':'Create new Proposal',
                                                'buttontext': 'Create and go to next step'})
    else:
        return render(request, 'GenericForm.html', {'form':form,
                                                'formtitle':'Create new Proposal (For next timeslot)',
                                                'buttontext': 'Create and go to next step'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_edit_proposal
def editProposal(request, pk):
    """
    Edit a given proposal. Only for staff that is allowed to edit the proposal. Timeslot validation is handled in form.

    :param request:
    :param pk: pk of the proposal to edit.
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if request.method == 'POST':
        form = ProposalFormEdit(request.POST, request.FILES, request=request, instance=obj)
        if form.is_valid():
            obj = form.save()
            if form.changed_data:
                updatePropCache(obj)
                if obj.Private.all():
                    for std in obj.Private.all():
                        mailPrivateStudent(request, obj, std, "Your private proposal was edited.")
            return render(request, "proposals/ProposalMessage.html", {"Message": "Proposal saved!", "Proposal": obj})
    else:
         form = ProposalFormEdit(request=request, instance=obj)
    return render(request, 'GenericForm.html', {'form': form, 'formtitle': 'Edit Proposal', 'buttontext': 'Save'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_view_proposal
def copyProposal(request, pk):
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

            mailAffectedUser(request, prop)
            if prop.Private.all():
                for std in prop.Private.all():
                    mailPrivateStudent(request, prop, std, "A private proposal was created for you.")
            return render(request, "proposals/ProposalMessage.html", {"Message": "Proposal created!", "Proposal": prop})
    else:
        oldproposal = get_object_or_404(Proposal, pk=pk)
        oldproposal.id = None
        # default timeslot. Overridden by form if this is not in phase 1.
        oldproposal.TimeSlot = get_timeslot()

        # Assistants and privates are removed, because m2m is not copied in this way.
        form = ProposalFormCreate(request=request, instance=oldproposal)
    if get_timephase_number() == 1:
        return render(request, 'GenericForm.html', {'form': form,
                                                    'formtitle': 'Edit copied proposal',
                                                    'buttontext': 'Create and go to next step'})
    else:
        return render(request, 'GenericForm.html', {'form': form,
                                                    'formtitle': 'Edit copied proposal (For next timeslot)',
                                                    'buttontext': 'Create and go to next step'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_edit_proposal
def addFile(request, pk, ty):
    """
    Add a file of type ty to a proposal. The type can be an image or a file (usually pdf). The image is shown in an
    image slider, an attachement is shown as a download button.

    :param request:
    :param pk: pk of the proposal
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
            return render(request, "proposals/ProposalMessage.html", {"Message": "File to Proposal saved! Click the button below to add another file.", "Proposal" : obj})
    #else:
    #    form = ProposalImageFormAdd(request=request, instance=obj)
    return render(request, 'GenericForm.html', {'form' : form, 'formtitle': 'Add ' + ty + ' to Proposal '+obj.Title, 'buttontext': 'Save'})


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_edit_proposal
def editFile(request, pk, ty):
    """
    Edit a file of a proposal.

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

    formSet = modelformset_factory(model, form=form, can_delete=True, extra=0)
    qu = model.objects.filter(Proposal=obj)

    formset = formSet(queryset=qu)

    if request.method == 'POST':
        formset = formSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render(request, "proposals/ProposalMessage.html", {"Message": "File changes saved!", "Proposal" : obj})
    return render(request, 'GenericForm.html', {'formset': formset, 'formtitle': 'All ' + ty + 's in Proposal '+obj.Title, "Proposal": obj.pk, 'buttontext': 'Save changes'})


@group_required('type3staff')
def askDeleteProposal(request, pk):
    """
    A confirmform for type3staff to delete a proposal. Regular staff cannot delete a proposal, as this should not
    happen. Public (=status4) proposals cannot be deleted.

    :param request:
    :param pk: pk of proposal to delete.
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if obj.Status >= 3:
        return render(request, "proposals/ProposalMessage.html", {"Message" : "This Proposal is already approved or public, it cannot be deleted", "Proposal" : obj},
                      status=403)
    form = "<a href="+reverse('proposals:deleteproposal', kwargs={"pk":int(pk)})+" class='button warning'><span class='mif-bin'></span>click here to DELETE</a></button></form>"
    return render(request, "proposals/ProposalMessage.html", {"Message": "Are you sure to delete? This cannot be undone " + form, "Proposal" : obj})


@group_required('type3staff')
def deleteProposal(request, pk):
    """
    Really delete a proposal. This can only be called by type3staff after going to the confirm delete page.

    :param request:
    :param pk: pk of the proposal to delete
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    if obj.Status >= 3:
        return render(request, "proposals/ProposalMessage.html", {"Message" : "Proposal is locked for editing", "Proposal" : obj},
                      status=403)

    if "HTTP_REFERER" in request.META:
        if (request.META["HTTP_REFERER"].split('/'))[-3] == "askdelete":
            # make sure previous page is askdelete
            title = obj.Title
            obj.delete()
            return render(request, "proposals/ProposalMessage.html", {"Message": "Proposal " + title + " is removed", "return" : ""})
    raise PermissionDenied("You should not access this page directly")


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
def chooseEditProposal(request):
    """
    This lists all proposals that the given user has something to do with. Either a responsible or assistant. For
    Type3staff this lists all proposals. This is the ussual view for staff to view their proposals.

    :param request:
    :return:
    """
    # show projects from all timeslots, filtering through datatables.
    allprops = Proposal.objects.all()
    proposals = []

    if get_grouptype("3") in request.user.groups.all():
        proposals = list(allprops)
    else:
        for prop in allprops:
            if request.user == prop.ResponsibleStaff or request.user in prop.Assistants.all():
                proposals.append(prop)

    return render(request, 'proposals/ProposalsCustomList.html', {"proposals": proposals})


@login_required
def upgradeStatus(request, pk):
    """
    Upgrade the status of a given proposal.

    :param request:
    :param pk: pk of the proposal to upgrade
    :return:
    """
    obj = get_object_or_404(Proposal, pk=pk)
    r = upgradeStatusApi(request, pk)
    return render(request, "proposals/ProposalMessage.html", {"Message" : r.content, "Proposal":obj},
                  status=r.status_code)


@can_downgrade_proposal
def downgradeStatusMessage(request, pk):
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
            form = ProposalDowngradeMessageForm(request.POST) # , request=request
            if form.is_valid():
                message = form.cleaned_data['Message']
                r = downgradeStatusApi(request, pk, message)
                notify = r.content.decode()
                if message != '':
                    notify += "<br />With note: <br />" + str(message)
                return render(request, "proposals/ProposalMessage.html", {"Message": notify, "Proposal": obj},
                              status=r.status_code)
        else:
            form = ProposalDowngradeMessageForm()  # request=request
            return render(request, 'GenericForm.html',
                      {'form': form, 'formtitle': 'Message for downgrade proposal '+obj.Title, 'buttontext': 'Downgrade and send message'})
    else:
        r = downgradeStatusApi(request, pk)
        return render(request, "proposals/ProposalMessage.html", {"Message": r.content.decode(), "Proposal": obj},
                      status=r.status_code)


@group_required('type1staff', 'type2staff', 'type2staffunverified')
def pending(request):
    """
    Get and show the pending proposals for a given user.

    :param request:
    :return:
    """
    props = []
    if get_grouptype("2")in request.user.groups.all() or get_grouptype("2u") in request.user.groups.all():
        props = get_all_proposals().filter(Q(Assistants__id=request.user.id) & Q(Status__exact=1))

    elif get_grouptype("1") in request.user.groups.all():
        props = get_all_proposals().filter((Q(ResponsibleStaff=request.user.id) & Q(Status__exact=2)) |
                                       (Q(Track__Head=request.user.id) & Q(Status__exact=3)))

    return render(request, "proposals/pendingProposals.html", {"proposals":props})


@group_required('type1staff')
def listTrackProposals(request):
    """
    List all proposals of the track that the user is head of.

    :param request:
    :return:
    """
    if not Track.objects.filter(Head=request.user).exists():
        raise PermissionDenied("This page is only for track heads.")
    objs = Track.objects.filter(Head__id=request.user.id)
    props = get_all_proposals().filter(Track__in=objs)
    return render(request, "proposals/ProposalsCustomList.html", {
        "proposals" : props,
        "title"     : "Proposals of my Track"
    })


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
@can_edit_proposal
def getShareLink(request, pk):
    """
    Get a sharelink for a given proposal. This link is a public view link for a proposal-detailpage for when the
    proposal is not yet public.

    :param request:
    :param pk: Proposal pk to get sharelink for
    :return:
    """
    link = createShareLink(request, pk)
    return render(request, "base.html", {
        "Message" : "Sharelink created: <a href=\"{}\">{}</a> <br/> Use this to show the proposal to anybody without an account. "
                    "The link will be valid for seven days.".format(link, link),
    })


def truncatestring(data, trunlen=10):
    """

    :param data:
    :param trunlen:
    :return:
    """
    return (data[:trunlen] + '..') if len(data) > trunlen else data


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
def getProposalStats(request, step=0):
    """
    Gives an overview of the statistics of the proposals of the user. These include the ammount of visitors and applications.
    This is only for timephase 5 and later

    :param request:
    :param step: integer, which step of the wizard view you want to see, supplied via URI
    :return:
    """
    if get_timephase_number() < 6:
        raise PermissionDenied("Proposals statistics are only available from timephase 6 onwards.")
    step = int(step)
    allprops = get_all_proposals().filter(Status=4).order_by('-Title')
    proposals = []

    if get_grouptype("3") in request.user.groups.all():
        proposals = list(allprops)
    else:
        for prop in allprops:
            if request.user == prop.ResponsibleStaff or request.user in prop.Assistants.all():
                proposals.append(prop)

    if step == 0:
        return render(request, "proposals/ProposalStats.html", {"step" : 0})
    elif step == 1:
        counts = []
        tabledata = []
        for p in proposals:
            try:
                counts.append(p.tracking.UniqueVisitors.count())
            except:
                counts.append(0)
            try:
                tabledata.append({
                    "prop" : p,
                    "count" : p.tracking.UniqueVisitors.count()
                })
            except:
                tabledata.append({
                    "prop" : p,
                    "count" : 0
                })
        return render(request, "proposals/ProposalStats.html", {
            "counts" : counts,
            "labels" : [truncatestring(p.Title) for p in proposals],
            "tabledata" : tabledata,
            "step"   : 1
        })
    else:
        if step - 3 >= len(proposals):
            return render(request, "proposals/ProposalStats.html", {"step" : -1})
        prop = proposals[step - 3]
        try:
            count =  prop.tracking.UniqueVisitors.count()
        except:
            count = 0

        return render(request, "proposals/ProposalStats.html", {
            "prop": prop,
            "visitors": count,
            "applications": [
                prop.applications.filter(Priority=1).count(),
                prop.applications.filter(Priority=2).count(),
                prop.applications.filter(Priority=3).count(),
                prop.applications.filter(Priority=4).count(),
                prop.applications.filter(Priority=5).count(),
            ],
            "distributed" : prop.distributions.count(),
            "step" : step
        })


@group_required('type1staff', 'type2staff', 'type2staffunverified', 'type3staff')
def getProposalStatsGeneral(request, step=0):
    """
    Provides report of general statistics, this is breakdown per group etc and the top10 of proposals on the marketplace.
    Only for timephase  5 and 6

    :param request:
    :param step: integer, which step of the wizard view you want to see, supplied via URI
    :return:
    """

    if get_timephase_number() < 6:
        raise PermissionDenied("Proposals statistics are only available from timephase 6 onwards.")
    step = int(step)

    if step == 0:
        return render(request, "proposals/ProposalStatsGeneral.html", {"step" : 0})
    elif step == 1:
        groupcount = []

        for group in GroupOptions:
            groupcount.append(get_all_proposals().filter(Q(Status=4) & Q(Group=group[0])).distinct().count())

        return render(request, "proposals/ProposalStatsGeneral.html", {
            "proposalcount": get_all_proposals().filter(Status=4).count(),
            "groupcount": groupcount,
            "groups" : [g[0] for g in GroupOptions],
            "step" : 1,
        })
    elif step == 2:
        trackcount = []
        for track in Track.objects.all():
            trackcount.append(get_all_proposals().filter(Q(Status=4) & Q(Track=track)).distinct().count())
        return render(request, "proposals/ProposalStatsGeneral.html", {
            "step" : 2,
            "tracks" : [t.Name for t in Track.objects.all()],
            "trackcount" : trackcount,
        })
    elif step > 12:
        return render(request, "proposals/ProposalStatsGeneral.html", {"step": -1})
    else:
        prop = get_all_proposals()\
                   .annotate(d_count=Count('distributions', distinct=True))\
                   .annotate(a_count=Count('applications', distinct=True))\
                   .order_by('-d_count', '-a_count')[step - 3]
        try:
            count =  prop.tracking.UniqueVisitors.count()
        except:
            count = 0
        return render(request, "proposals/ProposalStatsGeneral.html", {
            "prop": prop,
            "visitors": count,
            "applications": [
                prop.applications.filter(Priority=1).count(),
                prop.applications.filter(Priority=2).count(),
                prop.applications.filter(Priority=3).count(),
                prop.applications.filter(Priority=4).count(),
                prop.applications.filter(Priority=5).count(),
            ],
            "distributed" : prop.distributions.count(),
            "step" : step
        })