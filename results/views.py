from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from BepMarketplace.decorators import group_required, phase_required
from general_form import ConfirmForm
from general_view import get_grouptype
from students.models import Distribution
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number
from .forms import MakeVisibleForm, GradeCategoryForm, GradeCategoryAspectForm, AspectResultForm, CategoryResultForm
from .models import GradeCategory, CategoryResult, CategoryAspectResult, GradeCategoryAspect, ResultOptions


@group_required('type1staff', 'type3staff')
@phase_required(6, 7)
def finalize(request, pk, version=0):
    """
    Finalize the grades and print. Only for assessors.

    :param version:
    :param request:
    :param pk:
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'resultoptions'):
        raise PermissionDenied("Results menu is not yet visible.")
    else:
        if not get_timeslot().resultoptions.Visible:
            raise PermissionDenied("Results menu is not yet visible.")


    dstr = get_object_or_404(Distribution, pk=pk)

    if not hasattr(dstr, 'presentationtimeslot'):
        raise PermissionDenied('This student does not have a presentation planned. Please plan it first.')

    if not request.user.is_superuser and \
            request.user not in dstr.presentationtimeslot.Presentations.Assessors.all() and \
            request.user != dstr.Proposal.Track.Head:
        raise PermissionDenied("You are not the correct owner of this distribution."
                               " Grades can only be finalized by assessors or track heads.")

    vals = [cat.is_valid() for cat in dstr.results.all()]
    if dstr.results.count() < GradeCategory.objects.filter(TimeSlot=get_timeslot()).count() or not all(
            val is True for val in vals):
        return render(request, "base.html", context={
            "Message": "Not all categories and aspects have been filled in, please complete the grading first.",
            "return": "results:gradeformstaff",
            "returnget": str(pk),
        })
    version = int(version)
    if version == 0:  # The normal page summarizing the grades of the student
        return render(request, "results/printGrades.html", {
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "final": all(f.Final is True for f in dstr.results.all()),
            "finalgrade": dstr.TotalGradeRounded(),
        })
    elif version == 1:  # printable page with grades
        if get_timephase_number() != 7:
            raise PermissionDenied("Not yet possible to finalize in this timephase")
        for cat in dstr.results.all():
            # set final to True, disable editing from here onward.
            cat.Final = True
            cat.save()

        return render(request, "results/printGradesStandAlone.html", {
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "finalgrade": dstr.TotalGradeRounded(),
        })
    elif version == 2:  # pdf with grades
        if get_timephase_number() != 7:
            raise PermissionDenied("Not yet possible to finalize in this timephase")
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
@phase_required(6, 7)
def staff_form(request, pk, step=0):
    """
    Edit grade for a category as indexed by step. For each student as given by pk.
    Also edit the individual aspects of each grade category. For trackheads and responsible staff

    :param request:
    :param pk: id of distribution
    :param step: number of step in the menu, index of category
    :return:
    """
    ts = get_timeslot()
    if not hasattr(ts, 'resultoptions'):
        raise PermissionDenied("Results menu is not yet visible.")
    else:
        if not get_timeslot().resultoptions.Visible:
            raise PermissionDenied("Results menu is not yet visible.")

    dstr = get_object_or_404(Distribution, pk=pk)

    if not hasattr(dstr, 'presentationtimeslot'):
        raise PermissionDenied('This student does not have a presentation planned. Please plan it first.')

    if not request.user.is_superuser and \
            request.user != dstr.Proposal.Track.Head and \
            request.user != dstr.Proposal.ResponsibleStaff and \
            get_grouptype('3') not in request.user.groups.all() and \
            request.user not in dstr.presentationtimeslot.Presentations.Assessors.all():
        raise PermissionDenied("You are not the correct owner of this distribution. "
                               "Only track heads and responsible staff can edit grades.")

    cats = GradeCategory.objects.filter(TimeSlot=get_timeslot())
    numcategories = len(cats)
    step = int(step)
    if step == 0:
        return render(request, "results/wizard.html", {
            "step": 0,
            "pk": pk,
            "categories": cats,
            "dstr": dstr,
        })
    elif step <= numcategories:
        saved = False
        cat = cats[step - 1]
        try:
            catresult = CategoryResult.objects.get(Distribution=dstr, Category=cat)
        except:
            catresult = CategoryResult(Distribution=dstr, Category=cat)
        if request.method == "POST":
            if catresult.Final:
                return render(request, "base.html", status=410, context={
                    "Message": "Category Result has already been finalized! Editing is not allowed anymore. "
                               "If this has to be changed, contact support staff"
                })
            categoryform = CategoryResultForm(request.POST, instance=catresult, prefix='catform')
            aspectforms = []

            for i, aspect in enumerate(cat.aspects.all()):
                try:
                    aspresult = CategoryAspectResult.objects.get(CategoryResult=catresult, CategoryAspect=aspect)
                except:
                    aspresult = CategoryAspectResult(CategoryResult=catresult, CategoryAspect=aspect)
                aspectforms.append({
                    "form": AspectResultForm(request.POST, instance=aspresult, prefix="aspect" + str(i)),
                    "aspect": aspect,
                })

            vals = [form['form'].is_valid() for form in aspectforms]
            if categoryform.is_valid() and all(val is True for val in vals):
                catresult = categoryform.save()
                for form in aspectforms:
                    obj = form['form'].instance
                    obj.CategoryResult = catresult
                    obj.save()
                saved = True

            return render(request, "results/wizard.html", {
                "step": step,
                "categories": cats,
                "category": cat,
                "categoryform": categoryform,
                "aspectsforms": aspectforms,
                "dstr": dstr,
                "pk": pk,
                "saved": saved,
                "final": catresult.Final,
                "aspectlabels": CategoryAspectResult.ResultOptions,
            })
        else:
            categoryform = CategoryResultForm(instance=catresult, prefix='catform', disabled=catresult.Final)
            aspectforms = []
            for i, aspect in enumerate(cat.aspects.all()):
                try:
                    aspresult = CategoryAspectResult.objects.get(CategoryResult=catresult, CategoryAspect=aspect)
                except:
                    aspresult = CategoryAspectResult(CategoryResult=catresult, CategoryAspect=aspect)
                aspectforms.append({
                    "form": AspectResultForm(instance=aspresult, prefix="aspect" + str(i), disabled=catresult.Final),
                    "aspect": aspect,
                })
            return render(request, "results/wizard.html", {
                "step": step,
                "categories": cats,
                "category": cat,
                "categoryform": categoryform,
                "aspectsforms": aspectforms,
                "dstr": dstr,
                "pk": pk,
                "saved": False,
                "final": catresult.Final,
                "aspectlabels": CategoryAspectResult.ResultOptions
            })
    else:
        raise PermissionDenied("This category does not exist.")


@login_required
def about(request, pk=None):
    """
    Explanation about grading and grade categories.

    :param request:
    :param pk: optional pk of a timeslot, only for support user.
    :return:
    """
    if pk and get_grouptype('3') in request.user.groups.all():
        ts = get_object_or_404(TimeSlot, pk=pk)
    else:
        ts = get_timeslot()
    return render(request, "results/about_grades.html", {
        'scores': CategoryAspectResult.ResultOptions,
        "categories": GradeCategory.objects.filter(TimeSlot=ts),
        'ts': ts,
    })


@group_required('type3staff')
def list_categories(request):
    """

    :param request:
    :return:
    """
    ts = get_timeslot()
    cats = GradeCategory.objects.filter(TimeSlot=ts)
    ws = cats.aggregate(Sum('Weight'))['Weight__sum']
    wsa = GradeCategoryAspect.objects.filter(Category__in=cats).count()

    if not hasattr(ts, 'resultoptions'):
        r = ResultOptions(
            TimeSlot=ts
        )
        r.save()

    r = ts.resultoptions

    if request.method == "POST":
        form = MakeVisibleForm(request.POST, instance=r)
        if form.is_valid():
            options = form.save()
            options.save()
    else:
        form = MakeVisibleForm(instance=r)

    return render(request, "results/list_categories.html", {
        "categories": GradeCategory.objects.filter(TimeSlot=ts),
        'ts': ts,
        'gsum': ws,
        'asum': wsa,
        'visible': r.Visible,
        'form': form,
    })


@group_required('type3staff')
def add_category(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = GradeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'base.html',
                          {'Message': 'Grade category added!',
                           'return': 'results:list_categories'})
    else:
        form = GradeCategoryForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add grade category',
        'buttontext': 'Save',
    })


@group_required('type3staff')
def edit_category(request, pk):
    """

    :param request:
    :param pk:
    :return:
    """
    category = get_object_or_404(GradeCategory, pk=pk)
    if request.method == 'POST':
        form = GradeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return render(request, 'base.html', {
                    'Message': 'Grade category saved!',
                    'return': 'results:list_categories',
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'Grade category unchanged.',
                    'return': 'results:list_categories',
                })
    else:
        form = GradeCategoryForm(instance=category)

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit grade category',
        'buttontext': 'Save',
    })


@group_required('type3staff')
def delete_category(request, pk):
    """

    :param request:
    :param pk:
    :return:
    """
    cat = get_object_or_404(GradeCategory, pk=pk)
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            for aspect in cat.aspects.all():
                aspect.delete()
            cat.delete()
            return render(request, 'base.html', {
                'Message': 'Grade category deleted.',
                'return': 'results:list_categories',
            })
    else:
        form = ConfirmForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Delete grade category?',
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def list_aspects(request, pk):
    """
    List all aspects of a given grade category in the current timeslot

    :param request:
    :param pk: pk of grade category
    :return:
    """
    category = get_object_or_404(GradeCategory, pk=pk)
    aspects = GradeCategoryAspect.objects.filter(Category=category)
    ts = get_timeslot()
    return render(request, "results/list_aspects.html", {
        "aspects": aspects,
        'ts': ts,
        'cat': category,
    })


@group_required('type3staff')
def add_aspect(request, pk):
    """

    :param request:
    :param pk:
    :return:
    """
    category = get_object_or_404(GradeCategory, pk=pk)
    if request.method == 'POST':
        form = GradeCategoryAspectForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.Category = category
            f.save()
            return render(request, 'base.html',
                          {'Message': 'Grade category aspect added!',
                           'return': 'results:list_aspects',
                           'returnget': category.pk})
    else:
        form = GradeCategoryAspectForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Add grade category aspect to ' + category.Name,
        'buttontext': 'Save',
    })


@group_required('type3staff')
def edit_aspect(request, pk):
    """

    :param request:
    :param pk:
    """
    aspect = get_object_or_404(GradeCategoryAspect, pk=pk)
    if request.method == 'POST':
        form = GradeCategoryAspectForm(request.POST, instance=aspect)
        if form.is_valid():
            if form.has_changed():
                form.save()
                return render(request, 'base.html', {
                    'Message': 'Grade category aspect saved!',
                    'return': 'results:list_aspects',
                    'returnget': aspect.Category.id,
                })
            else:
                return render(request, 'base.html', {
                    'Message': 'Grade category aspect unchanged.',
                    'return': 'results:list_aspects',
                    'returnget': aspect.Category.id,
                })
    else:
        form = GradeCategoryAspectForm(instance=aspect)

    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Edit grade category aspect of ' + aspect.Category.Name,
        'buttontext': 'Save',
    })


@group_required('type3staff')
def delete_aspect(request, pk):
    """

    :param request:
    :param pk:
    :return:
    """
    aspect = get_object_or_404(GradeCategoryAspect, pk=pk)
    cat = aspect.Category.id
    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            aspect.delete()
            return render(request, 'base.html', {
                'Message': 'Grade category aspect deleted.',
                'return': 'results:list_aspects',
                'returnget': cat})
    else:
        form = ConfirmForm()
    return render(request, 'GenericForm.html', {
        'form': form,
        'formtitle': 'Delete grade category aspect?',
        'buttontext': 'Confirm'
    })


@group_required('type3staff')
def copy(request, pk=None):
    """
    Show a list of timeslots to import grades from.

    :param request:
    :param pk:
    :return:
    """
    # do a copy
    if pk:
        ts = get_object_or_404(TimeSlot, pk=pk)
        if ts == get_timeslot():
            raise PermissionDenied("It is not possible to copy the grades from the current timeslot.")
        if get_timeslot().gradecategories.exists():
            return render(request, 'base.html', {
                'Message': "The current timeslot already has grade categories."
                           " Importing is not possible. "
                           "Please remove the categories in the current timeslot before copying.",
                'return': 'results:list_categories'})

        if request.method == 'POST':
            form = ConfirmForm(request.POST)
            if form.is_valid():
                for cat in ts.gradecategories.all():
                    old_id = cat.id
                    old_aspects = cat.aspects.all()
                    cat.id = None
                    cat.TimeSlot = get_timeslot()
                    cat.save()
                    for aspect in old_aspects:
                        aspect.id = None
                        aspect.Category = cat
                        aspect.save()

                return render(request, 'base.html',
                              {'Message': 'Finished importing!', 'return': 'results:list_categories'})
        else:
            form = ConfirmForm()
        return render(request, 'GenericForm.html', {
            'form': form,
            'formtitle': 'Confirm copy grade categories and aspects',
            'buttontext': 'Confirm'
        })
    # list possible timeslots to copy from
    else:
        tss = TimeSlot.objects.filter(gradecategories__isnull=False).distinct()
        return render(request, "results/list_copy.html", {
            "tss": tss,
            'ts': get_timeslot(),
        })
