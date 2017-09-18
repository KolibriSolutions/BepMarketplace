import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

import general_excel
from BepMarketplace.decorators import group_required
from general_form import print_formset_errors
from general_view import get_timephase_number, get_grouptype
from index.models import Track
from students.models import Distribution
from .forms import PresentationOptionsForm, PresentationRoomForm, PresentationSetForm, get_timeslot, MakePublicForm
from .models import Room, PresentationSet, PresentationTimeSlot


@group_required("type3staff")
def presentationswizardstep1(request):
    """
    Step 1 of the planning of the presentations for the projects.
    In this step global options are set, these are only for validation and can be overridden per presentation afterwards.

    :param request: 
    :return: 
    """
    ts = get_timeslot()
    try:
        options = ts.presentationoptions
    except:
        options = None
    if request.method == 'POST':
        form = PresentationOptionsForm(request.POST, instance=options)
        if form.is_valid():
            #if something changed or if nothing exists yet.
            if form.changed_data or not hasattr(ts, 'presentationoptions'):
                # create new
                options = form.save()
                try:
                    options.Timeslot = get_timeslot()
                # check for errors
                    options.validate_unique()
                except:
                    return render(request, "base.html", {
                        "Message": "Presentation options failed. Please try again or contact support staff.", "return":reverse("presentations:presentationswizardstep2")})
                options.save()
                return render(request, "base.html", {"Message": "Presentation options saved. <br />\
                If there were already presentations planned and you changed the durations, please recalculate the timings in 'step 4' and re-save the presentations! \
                <br /><a class='button success' href='"+reverse("presentations:presentationswizardstep2")+"'>Go to next step</a>"})

            return render(request, "base.html", {"Message": "No changes in presentation options. <br />\
            <a class='button success' href='"+reverse("presentations:presentationswizardstep2")+"'>Go to next step</a>"})
    else:
        form = PresentationOptionsForm(instance=options)
    return render(request, 'GenericForm.html', {'form' : form, 'formtitle':'Presentations step 1; Presentation options', 'buttontext': 'Save and go to step 2'})


@group_required("type3staff")
def presentationswizardstep2(request):
    """
    Step 2 of the planning of the presentations for the projects.
    In this step the rooms for the presentations are set. Rooms have just a name. All used rooms have to be supplied.
    
    :param request:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {"Message": "There are no presentation options yet, please <a class='button success' href='"+reverse("presentations:presentationswizardstep1")+"'>go back to step 1</a>"})

    formSet = modelformset_factory(Room, form=PresentationRoomForm, can_delete=True, extra=6)
    formset = formSet(queryset=Room.objects.all())
    if request.method == 'POST':
        formset = formSet(request.POST)

        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "Rooms saved!  <br />\
            <a class='button success' href='"+reverse("presentations:presentationswizardstep3")+"'>Go to next step</a> <a class='button primary' href='"+reverse("presentations:presentationswizardstep2")+"'>Add more rooms</a>"})
        return render(request, "base.html",
                      {"Message": "Error in saving rooms: "+print_formset_errors(formset.errors)})
    else:
        return render(request, 'GenericForm.html', {'formset': formset, 'formtitle': "Presentations step 2; Rooms for presentations & assessments", 'buttontext': 'Save and go to step 3'})


@group_required("type3staff")
def presentationswizardstep3(request):
    """
    Step 3 of the planning of the presentations for the projects.
    Setting the presentation sets. A set of presentations is a fixed combination of a presentation room, an 
    assessment room, a track and a begin datetime. If any of these changes, a new set has to be made.
     
    :param request:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'presentationoptions'):
        return render(request, "base.html", {"Message": "There are no presentation options yet, please <a class='button success' href='"+reverse("presentations:presentationswizardstep1")+"'>go back to step 1</a>"})
    #this is needed because the form validation uses the presentation timeslot
    try:
        ts.timephases.get(Description=7)
    except:
        raise PermissionDenied("There is no timephase for presentations defined, please define a timephase or contact the support staff.")

    form = PresentationSetForm
    formSet = modelformset_factory(PresentationSet, form=form, can_delete=True, extra=4)
    formset = formSet(queryset=PresentationSet.objects.all())

    if request.method == 'POST':
        formset = formSet(request.POST)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html", {"Message": "Sets saved! <br />\
            If there were already presentations planned and you changed the durations, please recalculate the timings in 'step 4' and re-save the presentations! <br /> \
             <a class='button success' href='"+reverse("presentations:presentationswizardstep4")+"'>Go to final step</a> <a class='button primary' href='"+reverse("presentations:presentationswizardstep3")+"'>Make more sets</a>"})
        return render(request, "base.html",
                      {"Message": "Error in saving sets: "+print_formset_errors(formset.errors)})
    else:
        return render(request, 'GenericForm.html', {'formset': formset, 'formtitle': "Presentations step 3; Generate presentations sets", 'buttontext': 'Save and go to step 4'})


@group_required("type3staff")
def presentationswizardstep4(request):
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
        return render(request, "base.html", {"Message": "There are no presentation options yet, please <a class='button success' href='"+reverse("presentations:presentationswizardstep1")+"'>go back to step 1</a>"})
    if ts.presentationoptions.presentationsets.count() == 0:
        return render(request, "base.html", {
            "Message": "There are no presentation sets yet, please <a class='button success' href='" + reverse(
                "presentations:presentationswizardstep3") + "'>go back to step 3</a>"})
    if request.method == "POST":
        jsondata = request.POST.get('jsondata', None)
        if jsondata is None:
            return HttpResponse('{"type":"error","txt":"Invalid POST data"}')
        distobjs = json.loads(jsondata)
        #remove all current presentations
        for slot in PresentationTimeSlot.objects.filter(Presentations__PresentationOptions__TimeSlot=get_timeslot()):
            slot.delete()
        #generate new
        for set in distobjs:
#            print(set)
            setID = set[0]
            for slot in set[1]:
                slotObj = PresentationTimeSlot()
                slotObj.DateTime = datetime.fromtimestamp(slot['DateTime'])
                if slot['CustomType']:
                    slotObj.CustomDuration = slot['CustomDuration']
                    slotObj.CustomType = slot["CustomType"]
                else:
                    slotObj.Distribution = Distribution.objects.get(id=slot["Distribution"])
                slotObj.Presentations = PresentationSet.objects.get(id=setID)
                slotObj.validate_unique()
                slotObj.save()
        return HttpResponse('{"type":"success","txt":"success"}')
    else:
        dists = Distribution.objects.filter(Q(presenationtimeslot__isnull=True) & Q(Timeslot=get_timeslot()))
        sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts)
        opts = ts.presentationoptions
        types = PresentationTimeSlot.SlotTypes
        tracks = Track.objects.all()
        return render(request, 'presentations/planPresentations.html', {'dists': dists, 'sets': sets, 'opts': opts, 'types': types, 'tracks':tracks})


@group_required('type3staff')
def presentationsPlanning(request):
    """
    Table view of all presentations in this timeslot. Way too much unorganized information, so mostly used for debugging
    therefore only visible for type3staff
    
    :param request:
    :return:
    """
    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=get_timeslot())
    if not sets:
        return render(request, "base.html", {"Message": "There is nothing planned yet. Please plan the presentations first."})
    return render(request, "presentations/listPresentationsPlanning.html",{"sets": sets})


@login_required
def presentationsPlanningXls(request):
    """
    Shows the presentations planning in an Excel file in the same way as was done before the marketplace
    
    :param request:
    :return: xlsx file
    """
    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=get_timeslot())
    if not sets:
        return render(request, "base.html",
                      {"Message": "There is nothing planned yet. Please plan the presentations first."})

    file = general_excel.listPresentationsXls(sets)
    response = HttpResponse(content=file)
    response['Content-Disposition'] = 'attachment; filename=presentations-planning.xlsx'
    return response


@login_required
def presentationsCalendar(request):
    """
    Calendar view of the presentations planning, public visible in phase 7, otherwise only if 'public==True'
    
    :param request:
    :return:
    """
    if get_timephase_number() != 7:
        if get_grouptype("3") not in request.user.groups.all():
            try:
                public = get_timeslot().presentationoptions.Public
            except:
                raise PermissionDenied("Presentations are not yet planned.")
            if not public:
                raise PermissionDenied("Presentationsview is not yet open for public")

    ts = get_timeslot()
    sets = PresentationSet.objects.filter(PresentationOptions__TimeSlot=ts).order_by('DateTime')

    if not sets:
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
        return render(request, "presentations/presentationsCalendar.html", {"sets": sets, "form": form, "beginCalendar": begin })

    # normal view for non-type3 staff
    return render(request, "presentations/presentationsCalendar.html", {"sets": sets, "beginCalendar": begin})