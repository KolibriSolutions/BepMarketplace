#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.safestring import mark_safe

from general_form import ConfirmForm
from general_model import print_list
from index.decorators import group_required
from index.models import UserMeta
from timeline.utils import get_timeslot
from .data import read_osiris_xlsx
from .forms import OsirisDataFileForm


@group_required('type3staff')
def uploadOsiris(request):
    if request.method == 'POST':
        form = OsirisDataFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.TimeSlot = get_timeslot()  # not used atm, just set to current
            obj.save()
            return render(request, 'base.html', {
                'Message': 'usermeta uploaded!',
                'return': 'osirisdata:list'
            })
    else:
        form = OsirisDataFileForm()
    return render(request, 'osirisdata/osiris_upload_form.html', {
        'form': form,
        'formtitle': 'Upload Osiris data XLSX'
    })


@group_required('type3staff')
def listOsiris(request):
    try:
        data, log = read_osiris_xlsx()
    except Exception as e:
        return render(request, 'base.html', {
            'Message': 'Retrieving Osiris data failed. Please upload a valid file. Error: {0}'.format(e),
            'return': 'index:index',
        })
    return render(request, 'osirisdata/listosiris.html', {
        'persons': data,
        'log': log,
    })


@group_required('type3staff')
def osirisToMeta(request):
    write_errors = []
    try:
        data, log = read_osiris_xlsx()
    except:
        return render(request, 'base.html', {
            'Message': 'Retrieving Osirisdata failed. Please upload a valid file.',
            'return': 'index:index',
        })

    if request.method == 'POST':
        count = 0
        form = ConfirmForm(request.POST)
        if form.is_valid():
            for p in data:
                try:
                    user = User.objects.get(email=p.email)
                except User.DoesNotExist:
                    write_errors.append('User {} skipped'.format(p.email))
                    continue
                try:
                    meta = user.usermeta
                except UserMeta.DoesNotExist:
                    meta = UserMeta()
                    user.usermeta = meta
                    meta.save()
                    user.save()
                if p.automotive:
                    meta.Study = 'Automotive'
                else:
                    meta.Study = 'Electrical Engineering'
                meta.Cohort = p.cohort
                meta.ECTS = p.ects
                meta.Studentnumber = p.idnumber
                meta.save()
                count += 1
            return render(request, 'base.html', {
                'Message': mark_safe('User meta updated for {} users. <br />'.format(count)+print_list(write_errors)),
                'return': 'osirisdata:list'
            })
    else:
        form = ConfirmForm()

    return render(request, 'osirisdata/osiris_to_meta_form.html', {
        'form': form,
        'formtitle': 'Confirm write to usermeta',
        'buttontext': 'Confirm'
    })
