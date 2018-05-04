from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render

from BepMarketplace.decorators import group_required
from .forms import TimePhaseForm, TimeSlotForm
from .models import TimeSlot, TimePhase
from .utils import get_timeslot, get_timephase


@group_required('type3staff')
def list_timeslots(request):
    """
    List all timeslots (years)

    :param request:
    :return:
    """
    tss = TimeSlot.objects.all()
    cur = get_timeslot()
    return render(request, 'timeline/list_timeslots.html', {'tss': tss, 'cur': cur, 'now': datetime.now().date()})


@group_required('type3staff')
def add_timeslot(request):
    """
    add a timeslot

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html',
                          {'Message': 'TimeSlot added!',
                           'return': 'timeline:list_timeslots'})
    else:
        form = TimeSlotForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add TimeSlot',
        'buttontext': 'Save',
        'skip_date_validate': True,
    })


@group_required('type3staff')
def edit_timeslot(request, timeslot):
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    if ts.End < datetime.now().date():
        raise PermissionDenied('This timeslot has already finished.')
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=ts)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return render(request, 'base.html', {
                    'Message': 'TimeSlot saved!',
                    'return': 'timeline:list_timeslots',
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'TimeSlot not edited.',
                    'return': 'timeline:list_timeslots',
                })
    else:
        form = TimeSlotForm(instance=ts)
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit timeslot',
        'buttontext': 'Save',
        'skip_date_validate': True,
    })


@group_required('type3staff')
def list_timephases(request, timeslot):
    """
    List all timephases of a timeslot

    :param request:
    :param timeslot:
    :return:
    """
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    ph = ts.timephases.all()
    cur = get_timephase()
    return render(request, 'timeline/list_timephases.html',
                  {'ts': ts, 'ph': ph, 'cur': cur, 'now': datetime.now().date()})


@group_required('type3staff')
def add_timephase(request, timeslot):
    """
    add a timephase to a timeslot

    :param request:
    :param timeslot:
    :return:
    """
    ts = get_object_or_404(TimeSlot, pk=timeslot)
    if ts.End < datetime.now().date():
        raise PermissionDenied('This timeslot has already finished.')

    if request.method == 'POST':
        form = TimePhaseForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html', {
                'Message': 'TimePhase added!',
                'return': 'timeline:list_timephases',
                'returnget': ts.pk,
            })
    else:
        form = TimePhaseForm(initial={'Timeslot': ts})
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add TimePhase',
        'buttontext': 'Save',
        'skip_date_validate': True,
    })


@group_required('type3staff')
def edit_timephase(request, timephase):
    """

    :param request:
    :param timephase: timephase to edit
    :return:
    """
    tp = get_object_or_404(TimePhase, pk=timephase)
    if tp.End < datetime.now().date():
        raise PermissionDenied('This TimePhase has already finished.')

    if request.method == 'POST':
        form = TimePhaseForm(request.POST, instance=tp)
        if form.is_valid():
            if form.has_changed():
                tp = form.save()
                return render(request, 'base.html', {
                    'Message': 'TimePhase saved!',
                    'return': 'timeline:list_timephases',
                    'returnget': tp.Timeslot.pk,
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'TimePhase not edited.',
                    'return': 'timeline:list_timephases',
                    'returnget': tp.Timeslot.pk,
                })
    else:
        form = TimePhaseForm(instance=tp)
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit TimePhase',
        'buttontext': 'Save',
        'skip_date_validate': True,
    })
