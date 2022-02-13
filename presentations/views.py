#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, ProtectedError
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from htmlmin.decorators import not_minified_response

from general_view import get_grouptype
from general_model import delete_object, print_list
from index.decorators import group_required
from index.models import Track
from students.models import Distribution
from timeline.decorators import phase_required
from timeline.models import TimePhase
from timeline.utils import get_timephase_number
from .exports import get_list_presentations_xlsx
from .forms import PresentationOptionsForm, PresentationRoomForm, PresentationSetForm, get_timeslot, MakePublicForm
from .models import Room, PresentationSet, PresentationTimeSlot, PresentationOptions, Room
from .utils import planning_public


@group_required("type3staff")
@phase_required(5, 6, 7)
def wizard_step1(request):
    """
    Step 1 of the planning of the presentations for the projects.
    In this step global options are set,
    these are only for validation and can be overridden per presentation afterwards.

    :param request:
    :return:
    """
    ts = get_timeslot()  # if no timeslot, the phase_required decorator blocks this view.
    try:
        options = ts.presentationoptions
    except PresentationOptions.DoesNotExist:
        options = None
    if request.method == 'POST':
        form = PresentationOptionsForm(request.POST, instance=options)
        if form.is_valid():
            # if something changed or if nothing exists yet.
            if form.changed_data or options is None:
                options = form.save()
                options.TimeSlot = ts
                options.save()
                return render(request, "base.html", {"Message": "Presentation options saved. <br />\
                If there were already presentations planned and you changed the durations, "
                                                                "please recalculate the timings in 'step 4' and re-save the presentations! \
                <br /><a class='button success' href='" + reverse(
                    "presentations:presentationswizardstep2") + "'>Go to next step</a>"})
            return render(request, "base.html", {"Message": "No changes in presentation options. <br />\
            <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep2") + "'>Go to next step</a>"})
    else:
        form = PresentationOptionsForm(instance=options)
    return render(request, 'GenericForm.html', {'form': form, 'formtitle': 'Presentations step 1; Presentation options',
                                                'buttontext': 'Save and go to step 2'})


@group_required("type3staff")
@phase_required(5, 6, 7)
def wizard_step2_edit(request, kind):
    """
    Step 2 of the planning of the presentations for the projects.
    In this step the rooms for the presentations are set. Rooms have just a name. All used rooms have to be supplied.

    :param request:
    :param kind: Add or edit.
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {
            "Message": "There are no presentation options yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep1") + "'>go back to step 1</a>"})

    if kind == 'add':
        qs = Room.objects.none()
        ex = 10
    elif kind == 'edit':
        qs = Room.objects.all()
        ex = 0
    else:
        raise PermissionDenied('Wrong kind, choose add or edit.')

    form_set = modelformset_factory(Room, form=PresentationRoomForm, can_delete=kind == 'edit', extra=ex)
    formset = form_set(queryset=qs)
    if request.method == 'POST':
        formset = form_set(request.POST)
        if formset.is_valid():
            try:
                formset.save()
            except ProtectedError as e:
                raise PermissionDenied('Room can not be deleted, as other objects depend on it. Please remove the others first. Depending objects: {}'.format(
                    print_list(e.protected_objects)))
            return render(request, "base.html", {"Message": "Rooms saved!", "return": "presentations:presentationswizardstep2"})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': "Presentations step 2; {} rooms for presentations & assessments".format(kind.capitalize()),
                   'buttontext': 'Save'})


@group_required("type3staff")
@phase_required(5, 6, 7)
def wizard_step2(request):
    """
    Step 2 of the planning of the presentations for the projects.
    In this step the rooms for the presentations are set. Rooms have just a name. All used rooms have to be supplied.
    This view lists the rooms.

    :param request:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {
            "Message": "There are no presentation options yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep1") + "'>go back to step 1</a>"})

    rooms = Room.objects.all()
    res = []
    for room in rooms:
        used = [set for set in PresentationSet.objects.filter(Q(PresentationRoom=room) | Q(AssessmentRoom=room))]
        years = set([set.PresentationOptions.TimeSlot for set in used])
        res.append([room, years, used])
    return render(request, "presentations/list_rooms.html", {'rooms': res})


@group_required("type3staff")
@phase_required(5, 6, 7)
def wizard_step3(request):
    """
    Step 3 of the planning of the presentations for the projects.
    Setting the presentation sets. A set of presentations is a fixed combination of a presentation room, an
    assessment room, a track and a begin datetime. If any of these changes, a new set has to be made.

    :param request:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {
            "Message": "There are no presentation options yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep1") + "'>go back to step 1</a>"})
    # this is needed because the form validation uses the presentation timeslot
    try:
        ts.timephases.get(Description=7)
    except TimePhase.DoesNotExist:
        return render(request, "base.html", {
            'Message':
                "There is no timephase for presentations defined, please define a timephase using the 'Timeline Edit' menu or contact the support staff."})

    form = PresentationSetForm
    form_set = modelformset_factory(PresentationSet, form=form, can_delete=True, extra=24)
    formset = form_set(
        queryset=PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts).prefetch_related('Assessors__usermeta', 'PresentationAssessors__usermeta'))

    if request.method == 'POST':
        formset = form_set(request.POST)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "Sets saved! <br />\
            If there were already presentations planned and you changed the durations, "
                                                            "please recalculate the timings in 'step 4' and re-save the presentations! <br /> \
             <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep4") + "'>Go to final step</a> <a class='button primary' href='" + reverse(
                "presentations:presentationswizardstep3") + "'>Make more sets</a>"})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': "Presentations step 3; Generate presentations sets",
                   'buttontext': 'Save and go to step 4'})


@group_required("type3staff")
@phase_required(5, 6, 7)
def wizard_step4(request):
    """
    Step 4 of the planning of the presentations for the projects.
    This is where the actual presentations get planned. All previous steps come together. Each set is a column in the
    page. Individual presentations are on the right side and can be dragged into a timeslot. Time differences are
    automatically calculated. Times for breaks or assesments can be manually adjusted.

    :param request:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {
            "Message": "There are no presentation options yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep1") + "'>go back to step 1</a>"})
    if not ts.presentationoptions.presentationsets.exists():
        return render(request, "base.html", {
            "Message": "There are no presentation sets yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep3") + "'>go back to step 3</a>"})
    if request.method == "POST":
        jsondata = request.POST.get('jsondata', None)
        if not jsondata:
            return JsonResponse({'type': 'error', 'txt': 'Invalid POST data. Please contact support staff.'})
        distobjs = json.loads(jsondata)
        # remove all current presentations
        for slot in PresentationTimeSlot.objects.filter(Presentations__PresentationOptions__TimeSlot=get_timeslot()):
            delete_object(slot)
        # generate new
        for dset in distobjs:
            #            print(dset)
            set_id = dset[0]
            for slot in dset[1]:
                slotObj = PresentationTimeSlot()
                slotObj.DateTime = datetime.fromtimestamp(slot['DateTime'])
                if slot['CustomType']:
                    slotObj.CustomDuration = slot['CustomDuration']
                    slotObj.CustomType = slot["CustomType"]
                else:
                    slotObj.Distribution = Distribution.objects.get(id=slot["Distribution"])
                slotObj.Presentations = PresentationSet.objects.get(id=set_id)
                slotObj.validate_unique()
                slotObj.save()
        return JsonResponse({'type': 'success', 'txt': 'Data saved!'})
    else:
        dists = Distribution.objects.filter(Q(presentationtimeslot__isnull=True) & Q(TimeSlot=get_timeslot())).order_by('Proposal__ResponsibleStaff__last_name',
                                                                                                                        'Proposal__Track', 'Student__last_name')
        sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts)  # always ordered by date.
        opts = ts.presentationoptions
        types = PresentationTimeSlot.SlotTypes
        tracks = Track.objects.all()
        return render(request, 'presentations/plan_presentations.html',
                      {'dists': dists, 'sets': sets, 'opts': opts, 'types': types, 'tracks': tracks})


@group_required('type3staff')
@phase_required(5, 6, 7)
def list_presentations(request):
    """
    Table view of all presentations in this timeslot. Way too much unorganized information, so mostly used for debugging
    therefore only visible for type3staff

    :param request:
    :return:
    """
    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=get_timeslot()).prefetch_related('timeslots__Distribution__Proposal__ResponsibleStaff__usermeta',
                                                                                                         'timeslots__Distribution__Proposal__Assistants__usermeta',
                                                                                                         'timeslots__Distribution__Student__usermeta',
                                                                                                         'Assessors__usermeta','PresentationAssessors__usermeta',)
    if not sets:
        return render(request, "base.html",
                      {"Message": "There is nothing planned yet. Please plan the presentations first."})
    return render(request, "presentations/list_presentations_planning.html", {
        "sets": sets,
        'hide_sidebar': True}
                  )


@not_minified_response
@login_required
def export_presentations(request):
    """
    Shows the presentations planning in an Excel file in the same way as was done before the marketplace

    :param request:
    :return: xlsx file
    """
    if get_timephase_number() <= 4:
        raise PermissionDenied("Projects are not yet distributed.")

    if get_timephase_number() != 7:
        if get_grouptype("3") not in request.user.groups.all():
            try:
                public = get_timeslot().presentationoptions.Public
            except:
                return render(request, 'base.html', {'Message': 'The Presentations are not yet planned.'})
            if not public:
                return render(request, 'base.html', {'Message': 'The Presentations planning is not yet public'})

    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=get_timeslot())
    if not sets:
        return render(request, "base.html",
                      {"Message": "There is nothing planned yet. Please plan the presentations first."})

    file = get_list_presentations_xlsx(sets)
    response = HttpResponse(content=file)
    response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response['Content-Disposition'] = 'attachment; filename=presentations-planning.xlsx'
    return response


@login_required
@phase_required(5, 6, 7)
def calendar(request, own=False):
    """
    Calendar view of the presentations planning, public visible in phase 7, otherwise only if 'public==True'

    :param request:
    :param own:
    :return:
    """
    if get_timephase_number() < 7 and get_grouptype("3") not in request.user.groups.all() and not planning_public():
        # in phase 5 and 6, planning is only visible for type3, except when it is set to public.
        return render(request, 'base.html', {'Message': 'The presentations planning is not yet public'})
    ts = get_timeslot()
    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts).order_by('DateTime')
    if own:
        sets = sets.filter(Q(timeslots__Distribution__Proposal__ResponsibleStaff=request.user) |
                           Q(timeslots__Distribution__Proposal__Assistants=request.user) |
                           Q(Assessors=request.user) |
                           Q(timeslots__Distribution__Student=request.user) |
                           Q(PresentationAssessors=request.user)).distinct()
    if not sets:
        if own:
            return render(request, "base.html", {"Message": "There are no presentations that you have to attend.",
                                                 'return': 'presentations:presentationscalendar'})
        else:
            return render(request, "base.html", {"Message": "The presentations are not yet planned."})

    # sets are ordered by datetime, so first set has the lowest time, this is where the calendar display starts
    begin = sets[0].DateTime.date()

    # To show a Make Public for the type3staff
    if get_grouptype("3") in request.user.groups.all() and get_timephase_number() != 7:

        if not hasattr(ts, 'presentationoptions'):
            return render(request, "base.html", {
                "Message": "There are no presentation options yet, please <a class='button success' href='" + reverse(
                    "presentations:presentationswizardstep1") + "'>go back to step 1</a>"})
        options = ts.presentationoptions
        if request.method == "POST":
            form = MakePublicForm(request.POST, instance=options)
            if form.is_valid():
                options = form.save()
                options.save()
        else:
            form = MakePublicForm(instance=options)
        return render(request, "presentations/presentations_calendar.html",
                      {"sets": sets, "form": form, "beginCalendar": begin})

    # normal view for non-type3 staff
    return render(request, "presentations/presentations_calendar.html",
                  {"sets": sets.prefetch_related('timeslots__Distribution__Proposal__Assistants__usermeta',
                                                 'timeslots__Distribution__Proposal__ResponsibleStaff__usermeta',
                                                 'timeslots__Distribution__Proposal__Track__Head__usermeta',
                                                 'Assessors__usermeta', 'PresentationAssessors__usermeta', ), "beginCalendar": begin, "own": own})
