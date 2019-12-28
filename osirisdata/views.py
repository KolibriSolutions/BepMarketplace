#  Bep Marketplace ELE
#  Copyright (c) 2016-2019 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.contrib.auth.models import User
from django.shortcuts import render

from index.decorators import group_required
from general_form import ConfirmForm
from index.models import UserMeta
from .data import osirisData


@group_required('type3staff')
def listOsiris(request):
    try:
        data = osirisData()
    except:
        return render(request, 'base.html', {
            'Message': 'Retrieving Osirisdata failed.',
            'return': 'index:index',
        })
    return render(request, 'osirisdata/listosiris.html', {
        'persons' : data.getalldata()
    })


@group_required('type3staff')
def osirisToMeta(request):
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            data = osirisData()
            for p in data.getalldata():
                try:
                    user = User.objects.get(email=p.email)
                except User.DoesNotExist:
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
                    meta.Study = 'Eletrical Engineering'
                meta.Cohort = p.cohort
                meta.ECTS = p.ects
                meta.Studentnumber = p.idnumber
                meta.save()
            return render(request, 'base.html', {
                'Message' : 'usermeta updated!',
                'return' : 'osirisdata:list'
            })
    else:
        form = ConfirmForm()

    return render(request, 'GenericForm.html', {
        'form' : form,
        'formtitle' : 'Confirm rewrite usermeta',
        'buttontext' : 'Confirm'
    })
