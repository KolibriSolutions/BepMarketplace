#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import json
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, render

from general_form import ConfirmForm
from general_model import print_list, delete_object
from index.decorators import group_required
from .forms import TimePhaseForm, TimeSlotForm, TimePhaseCopyForm, UserTimeSlotForm
from .models import TimeSlot, TimePhase
from .utils import get_timeslot


@group_required('type3staff')
def list_timeslots(request):
    """
    List all timeslots (years)

    :param request:
    :return:
    """
    tss = TimeSlot.objects.all()
    cur = get_timeslot()
    return render(request, 'timeline/list_timeslots.html',
                  {'tss': tss, 'cur': cur, 'now': datetime.now().date() - timedelta(days=settings.TIMELINE_EDIT_DAYS_AFTER_FINISH)})


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
    if ts.End < (datetime.now().date() - timedelta(days=settings.TIMELINE_EDIT_DAYS_AFTER_FINISH)):  # allow editing 30 days after timeslot ending.
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
    cur = get_timeslot()
    return render(request, 'timeline/list_timephases.html',
                  {'ts': ts, 'ph': ph, 'cur': cur, 'now': datetime.now().date() - timedelta(days=settings.TIMELINE_EDIT_DAYS_AFTER_FINISH)})


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
        form = TimePhaseForm(initial={'TimeSlot': ts})
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
    if tp.End < datetime.now().date() - timedelta(days=settings.TIMELINE_EDIT_DAYS_AFTER_FINISH):
        raise PermissionDenied('This TimePhase has already finished.')

    if request.method == 'POST':
        form = TimePhaseForm(request.POST, instance=tp)
        if form.is_valid():
            if form.has_changed():
                tp = form.save()
                return render(request, 'base.html', {
                    'Message': 'TimePhase saved!',
                    'return': 'timeline:list_timephases',
                    'returnget': tp.TimeSlot.pk,
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'TimePhase not edited.',
                    'return': 'timeline:list_timephases',
                    'returnget': tp.TimeSlot.pk,
                })
    else:
        form = TimePhaseForm(instance=tp)
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit TimePhase',
        'buttontext': 'Save',
        'skip_date_validate': True,
    })


@group_required('type3staff')
def copy_timephases(request):
    """
    Copy all timephases of one timeslot to the other timeslot

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = TimePhaseCopyForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['ts_from'].Begin
            to_date = form.cleaned_data['ts_to'].Begin
            diff = to_date - from_date
            copied = []
            for tp in form.cleaned_data['ts_from'].timephases.all().order_by("Description"):
                try:
                    tp.TimeSlot = form.cleaned_data['ts_to']
                    tp.id = None  # to make a copy.
                    tp.Begin = tp.Begin + diff
                    tp.End = tp.End + diff
                    if hasattr(tp, 'CountDownEnd'):
                        tp.CountDownEnd = tp.CountDownEnd + diff
                    tp.full_clean()
                    tp.save()
                    copied.append(tp.Description)
                except ValidationError as e:  # form save error, invalid dates
                    return render(request, 'base.html', {
                        'Message': 'TimePhases {} saved. Timephase {} could not be saved because of {}'.format(
                            print_list(copied), tp.Description,
                            print_list(e.messages)),
                        'return': 'timeline:list_timeslots',
                    })
            return render(request, 'base.html', {
                'Message': 'TimePhases {} saved! Please check and correct their Begin and End times manually.'.format(
                    print_list(copied)),
                'return': 'timeline:list_timeslots',
            })

    else:
        form = TimePhaseCopyForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Copy TimePhase',
        'buttontext': 'Copy',
    })


@group_required("type3staff")
def delete_timephase(request, timephase):
    """

    :param request:
    :param timephase: pk of timephase to delete
    :return:
    """
    name = 'Time phase'
    obj = get_object_or_404(TimePhase, pk=timephase)
    if obj.End < datetime.now().date():
        raise PermissionDenied('This TimePhase has already finished.')
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            delete_object(obj)
            return render(request, 'base.html', {
                'Message': '{} deleted.'.format(name),
                'return': 'timeline:list_timephases',
                'returnget': obj.TimeSlot.pk})
    else:
        form = ConfirmForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Delete {}?'.format(name),
        'buttontext': 'Delete'
    })


@group_required('type3staff')
def students(request):
    """
    Add a list of students to a specific timeslot

    :param request:
    :return:
    """

    if request.method == 'POST':
        form = UserTimeSlotForm(request.POST)
        if form.is_valid():
            ts = form.cleaned_data.get('timeslot')
            ss = form.cleaned_data.get('students')
            errors = []
            students = []
            for s in ss.strip().split():
                if s:
                    s = s.strip()
                    try:
                        student = User.objects.get(email=s)
                        if student.groups.exists():
                            errors.append(f'Email "{s}" is not a student. Skipped')
                            continue
                        students.append(student)
                    except User.DoesNotExist:
                        errors.append(f'Email "{s}" is not found.')
            data = {'ts': ts.pk, 'students': [s.pk for s in students]}
            return render(request, 'timeline/list_students_confirm.html', {
                'students': students,
                'errors': errors,
                'form': ConfirmForm(),
                'jsondata': json.dumps(data),
                'ts': ts,
            })
    else:
        form = UserTimeSlotForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add students to timeslot',
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def students_confirm(request):
    """
    Add a list of students to a specific timeslot

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            data = json.loads(request.POST.get('jsondata', None))
            if not data:
                raise PermissionDenied('Invalid data.')
            ts = get_object_or_404(TimeSlot, pk=data.get('ts'))
            cnt = 0
            for student in data['students']:
                s = get_object_or_404(User, pk=student, groups=None)
                s.usermeta.TimeSlot.add(ts)
                s.usermeta.save()
                cnt +=1
            return render(request, 'base.html', {
                'Message': f'{cnt} students set to {ts}.',
            })
        else:
            return render(request, 'base.html', {
                'Message': 'Please check confirm.',
            })
    else:
        raise PermissionDenied('Invalid request.')
