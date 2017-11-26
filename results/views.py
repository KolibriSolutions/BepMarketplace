from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa

from BepMarketplace.decorators import group_required, get_object_or_404
from BepMarketplace.decorators import phase7_only
from general_view import get_timeslot
from .forms import *
from django.core.exceptions import PermissionDenied

@group_required('type1staff', 'type3staff')
@phase7_only
def gradeFinalize(request, pk, version=0):
    """
    Finalize the grades and print. Only for trackheads.
    
    :param version: 
    :param request: 
    :param pk: 
    :return: 
    """
    dstr = get_object_or_404(Distribution, pk=pk)
    if not request.user.is_superuser and request.user != dstr.Proposal.Track.Head:
            raise PermissionDenied("You are not the correct owner of this distribution."\
                                     " Grades can only be finalized by track heads.")

    vals = [cat.is_valid() for cat in dstr.results.all()]
    if dstr.results.count() < GradeCategory.objects.filter(TimeSlot=get_timeslot()).count() or not all(val is True for val in vals):
        return render(request, "base.html", context={
            "Message" : "Not all categories and aspects have been filled in, please complete the grading first.",
            "return" : "results:gradeformstaff",
            "returnget": str(pk),
        })
    version = int(version)
    if version == 0:  # The normal page summarizing the grades of the student
        return render(request, "results/printGrades.html", {
            "dstr" : dstr,
            "catresults" : dstr.results.all(),
            "final" : all(f.Final is True for f in dstr.results.all()),
            "finalgrade" : dstr.TotalGradeRounded(),
        })
    elif version == 1:  # printable page with grades
        for cat in dstr.results.all():
            cat.Final = True
            cat.save()

        return render(request, "results/printGradesStandAlone.html", {
            "dstr" : dstr,
            "catresults" : dstr.results.all(),
            "finalgrade": dstr.TotalGradeRounded(),
        })
    elif version == 2:  # pdf with grades
        for cat in dstr.results.all():
            cat.Final = True
            cat.save()

        template = get_template('results/printGradesStandAlone.html')

        htmlblock = template.render({
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "finalgrade": dstr.TotalGradeRounded(),
        })

        buffer = BytesIO()
        pisaStatus = pisa.CreatePDF(htmlblock.encode('utf-8'), dest=buffer, encoding='utf-8')
        buffer.seek(0)
        response = HttpResponse(buffer, 'application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bepresult_{}.pdf"'.format(dstr.Student.get_full_name())
        return response


@group_required('type1staff', 'type3staff')
@phase7_only
def gradeFormStaff(request, pk, step=0):
    """
    Edit grade for a category as indexed by step. For each student as given by pk.
    Also edit the individual aspects of each grade category. Only for trackheads
    
    :param request: 
    :param pk: id of distribution
    :param step: number of step in the menu, index of category
    :return: 
    """
    dstr = get_object_or_404(Distribution, pk=pk)
    if not request.user.is_superuser and request.user != dstr.Proposal.Track.Head:
        raise PermissionDenied("You are not the correct owner of this distribution. "
                               "Only track heads can edit grades.")

    cats = GradeCategory.objects.filter(TimeSlot=get_timeslot())
    numcategories = len(cats)
    step = int(step)
    if step == 0:
        return render(request, "results/wizard.html", {
            "step" : 0,
            "pk": pk,
            "categories": cats,
            "dstr":dstr,
        })
    elif step <= numcategories:
        cat = cats[step - 1]
        try:
            catresult = CategoryResult.objects.get(Distribution=dstr, Category=cat)
        except:
            catresult = CategoryResult(Distribution=dstr, Category=cat)
        if request.method == "POST":
            if catresult.Final:
                return render(request, "base.html", status=410, context={
                    "Message" : "Category Result has already been finalized! Editing is not allowed anymore. "
                                "If this has to be lifted contact support staf"
                })
            categoryform = CategoryResultForm(request.POST, instance=catresult, prefix='catform')
            aspectforms = []
            for i, aspect in enumerate(cat.aspects.all()):
                try:
                    aspresult = CategoryAspectResult.objects.get(CategoryResult=catresult, CategoryAspect=aspect)
                except:
                    aspresult = CategoryAspectResult(CategoryResult=catresult, CategoryAspect=aspect)
                aspectforms.append({
                    "form" : AspectResultForm(request.POST, instance=aspresult, prefix="aspect" + str(i)),
                    "aspect" : aspect,
                })
            vals = [form['form'].is_valid() for form in aspectforms]
            if categoryform.is_valid() and all(val is True for val in vals):
                catresult = categoryform.save()
                for form in aspectforms:
                    obj = form['form'].instance
                    obj.CategoryResult = catresult
                    obj.save()
                return render(request, "results/wizard.html", {
                    "step": step,
                    "categories": cats,
                    "category": cat,
                    "categoryform": categoryform,
                    "aspectsforms": aspectforms,
                    "dstr": dstr,
                    "pk": pk,
                    "saved" : True,
                })
            else:
                return render(request, "results/wizard.html", {
                    "step": step,
                    "categories": cats,
                    "category": cat,
                    "categoryform": categoryform,
                    "aspectsforms": aspectforms,
                    "dstr": dstr,
                    "pk": pk,
                })
        else:
            categoryform = CategoryResultForm(instance=catresult, prefix='catform')
            aspectforms = []
            for i, aspect in enumerate(cat.aspects.all()):
                try:
                    aspresult = CategoryAspectResult.objects.get(CategoryResult=catresult, CategoryAspect=aspect)
                except:
                    aspresult = CategoryAspectResult(CategoryResult=catresult, CategoryAspect=aspect)
                aspectforms.append({
                    "form" : AspectResultForm(instance=aspresult, prefix="aspect" + str(i)),
                    "aspect" : aspect,
                })

            return render(request, "results/wizard.html", {
                "step" : step,
                "categories" : cats,
                "category" : cat,
                "categoryform" : categoryform,
                "aspectsforms" : aspectforms,
                "dstr" : dstr,
                "pk" : pk,
                "final" : catresult.Final,
            })
    else:
        raise Http404("This category does not exist.")


@login_required
def gradeExplanation(request):
    """
    Explanation about grading and grade categories.
    
    :param request: 
    :return: 
    """
    return render(request, "results/aboutgrades.html", {
        "categories" : GradeCategory.objects.filter(TimeSlot=get_timeslot())
    })
