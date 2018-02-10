from django.shortcuts import render
from .data import osirisData
from BepMarketplace.decorators import group_required
from django.contrib.auth.models import User
from index.models import UserMeta
from general_form import ConfirmForm

@group_required('type3staff')
def listOsiris(request):
    data = osirisData()
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
                meta.EnrolledBEP = p.enrolled
                meta.EnrolledExt = p.enrolledextension
                meta.Cohort = p.cohort
                meta.ECTS = p.ects
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