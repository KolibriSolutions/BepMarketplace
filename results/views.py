#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from io import BytesIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from general_form import ConfirmForm
from general_model import delete_object
from general_view import get_grouptype
from index.decorators import group_required
from students.models import Distribution
from timeline.decorators import phase_required
from timeline.models import TimeSlot
from timeline.utils import get_timeslot, get_timephase_number
from .forms import MakeVisibleForm, GradeCategoryForm, GradeCategoryAspectForm, AspectResultForm, CategoryResultForm  # , CategoryResultFormFile
from .models import GradeCategory, CategoryResult, CategoryAspectResult, GradeCategoryAspect, ResultOptions


@group_required('type1staff', 'type3staff')
@phase_required(6, 7)
def finalize(request, pk, version=0):
    """
    Finalize the grades and print. Only for assessors.

    :param request:
    :param pk: pk of Distribution to grade
    :param version: 0 for summary page, 1 for printable page, 2 for pdf export
    :return:
    """
    dstr = get_object_or_404(Distribution, pk=pk)
    ts = dstr.TimeSlot

    if ts != get_timeslot():
        raise PermissionDenied('This student is not from the current timeslot. Changing grades is not allowed.')

    if not hasattr(ts, 'resultoptions'):
        raise PermissionDenied("Results menu is not yet visible.")
    else:
        if not ts.resultoptions.Visible:
            raise PermissionDenied("Results menu is not yet visible.")

    dstr = get_object_or_404(Distribution, pk=pk)

    if not hasattr(dstr, 'presentationtimeslot'):
        raise PermissionDenied('This student does not have a presentation planned. Please plan it first.')

    if not request.user.is_superuser and \
            request.user not in dstr.presentationtimeslot.Presentations.Assessors.all() and \
            request.user != dstr.Proposal.Track.Head:
        raise PermissionDenied("You are not the correct owner of this distribution. "
                               " Grades can only be finalized by assessors or track heads. "
                               " To get a preview of the print view, use the 'Print Preview' button.")
    version = int(version)
    # check if grade is valid
    error_list = ''
    for cat in GradeCategory.objects.filter(TimeSlot=ts):
        try:
            cat_res = cat.results.get(Distribution=dstr)
            if not cat_res.is_valid():
                error_list += ('<li>Category {} is not completed.</li>'.format(cat))
        except CategoryResult.DoesNotExist:
            error_list += ('<li>Category {} is missing</li>'.format(cat))
    if error_list:
        return render(request, "base.html", context={
            'Message': '<h1>The results of this student are not yet finished</h1><p>The following error(s) occurred:</p><ul>{}</ul>'.format(error_list),
            "return": "results:gradeformstaff",
            "returnget": str(pk),
        })

    if version == 0:  # The normal page summarizing the grades of the student
        return render(request, "results/finalize_grades.html", {
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "final": all(f.Final is True for f in dstr.results.all()),
            "finalgrade": dstr.TotalGradeRounded(),
            "preview": False,
        })
    else:  # type 1 and 2, finalize grades.
        if get_timephase_number() != 7:
            raise PermissionDenied("Finalize grades is only possible in the time phase 'Presentation of results'")
        for cat in dstr.results.all():  # set final to True, disable editing from here onward.
            cat.Final = True
            cat.save()
        if version == 1:  # printable page with grades
            return render(request, "results/print_grades_pdf.html", {
                "dstr": dstr,
                "catresults": dstr.results.all(),
                "finalgrade": dstr.TotalGradeRounded(),
            })
        elif version == 2:  # pdf with grades
            html = get_template('results/print_grades_pdf.html').render({
                "dstr": dstr,
                "catresults": dstr.results.all(),
                "finalgrade": dstr.TotalGradeRounded(),
            })
            buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html.encode('utf-8'), dest=buffer, encoding='utf-8')
            if pisa_status.err:
                raise Exception("Pisa Failed PDF creation in print final grade for distribution {}.".format(dstr))
            buffer.seek(0)
            response = HttpResponse(buffer, 'application/pdf')
            response['Content-Disposition'] = 'attachment; filename="bepresult_{}.pdf"'.format(dstr.Student.usermeta.get_nice_name())
            return response
    raise PermissionDenied('Invalid type.')


@group_required('type1staff', 'type2staff', 'type3staff')
def finalize_preview(request, pk, version=0):
    """
    Edit grade for a category as indexed by step. For each student as given by pk.
    Also edit the individual aspects of each grade category. For trackheads and responsible staff

    :param request:
    :param pk: id of distribution
    :param version: 0 for summary page, 1 for printable page, 2 for pdf export
    :return:
    """
    dstr = get_object_or_404(Distribution, pk=pk)
    ts = dstr.TimeSlot
    old = bool(ts != get_timeslot())
    if not hasattr(ts, 'resultoptions'):
        raise PermissionDenied("Results menu is not yet available.")
    else:
        if not ts.resultoptions.Visible:
            raise PermissionDenied("Results menu is not yet visible.")
    if not old:  # current ts, check phase
        if get_timephase_number() != 6 and get_timephase_number() != 7:
            raise PermissionDenied('This page is only available in time phase "Execution of the projects" and "Presentation of results"')

    if not hasattr(dstr, 'presentationtimeslot'):
        raise PermissionDenied('This student does not have a presentation planned. Please plan it first.')
    if not request.user.is_superuser and \
            request.user != dstr.Proposal.Track.Head and \
            request.user != dstr.Proposal.ResponsibleStaff and \
            request.user not in dstr.Proposal.Assistants.all() and \
            get_grouptype('3') not in request.user.groups.all() and \
            request.user not in dstr.presentationtimeslot.Presentations.Assessors.all():
        raise PermissionDenied("You are not the correct owner of this distribution. "
                               "Only track heads, assistants, assessors and responsible staff can view grades.")

    if version == 0:
        return render(request, "results/finalize_grades.html", {
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "final": all(f.Final is True for f in dstr.results.all()) if dstr.results.all() else False,
            "finalgrade": dstr.TotalGradeRounded(),
            "preview": True,
        })
    elif version == 1:  # printable page with grades
        return render(request, "results/print_grades_pdf.html", {
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "finalgrade": dstr.TotalGradeRounded(),
            'preview': True,
        })
    elif version == 2:
        html = get_template('results/print_grades_pdf.html').render({
            "dstr": dstr,
            "catresults": dstr.results.all(),
            "finalgrade": dstr.TotalGradeRounded(),
            'preview': True,
        })
        buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html.encode('utf-8'), dest=buffer, encoding='utf-8')
        if pisa_status.err:
            raise Exception("Pisa Failed PDF creation in print final grade for distribution {}.".format(dstr))
        buffer.seek(0)
        response = HttpResponse(buffer, 'application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bepresult_{}.pdf"'.format(dstr.Student.usermeta.get_nice_name())
        return response


@group_required('type1staff', 'type2staff', 'type3staff')
def staff_form(request, pk, step=0):
    """
    Edit grade for a category as indexed by step. For each student as given by pk.
    Also edit the individual aspects of each grade category. For trackheads, assistants and responsible staff
    Used for pregrading as well as grading.

    :param request:
    :param pk: id of distribution
    :param step: number of step in the menu, index of category
    :return:
    """
    dstr = get_object_or_404(Distribution, pk=pk)
    ts = dstr.TimeSlot
    old = bool(ts != get_timeslot())

    if not hasattr(ts, 'resultoptions'):
        raise PermissionDenied("Results menu is not yet available.")
    else:
        if not ts.resultoptions.Visible:
            raise PermissionDenied("Results menu is not yet visible.")
    if not old:  # current ts, check phase
        if get_timephase_number() != 6 and get_timephase_number() != 7:
            raise PermissionDenied('This page is only available in time phase "Execution of the projects" and "Presentation of results"')

    if not hasattr(dstr, 'presentationtimeslot'):
        raise PermissionDenied('This student does not have a presentation planned. Please plan it first.')
    if not request.user.is_superuser and \
            request.user != dstr.Proposal.Track.Head and \
            request.user != dstr.Proposal.ResponsibleStaff and \
            request.user not in dstr.Proposal.Assistants.all() and \
            get_grouptype('3') not in request.user.groups.all() and \
            request.user not in dstr.presentationtimeslot.Presentations.Assessors.all():
        raise PermissionDenied("You are not the correct owner of this distribution. "
                               "Only track heads, assistants, assessors and responsible staff can change grades.")

    cats = GradeCategory.objects.filter(TimeSlot=ts).distinct()
    numcategories = len(cats)
    step = int(step)
    if step == 0:
        return render(request, "results/wizard.html", {
            "step": 0,
            "pk": pk,
            "categories": cats,
            "dstr": dstr,
            "final": all(f.Final is True for f in dstr.results.all()) if dstr.results.all() else False,  # fix for all([])=True
            'old': old,
            # "files": files,
        })
    elif step <= numcategories:
        saved = False
        cat = cats[step - 1]
        try:  # existing category result
            cat_result = CategoryResult.objects.get(Distribution=dstr, Category=cat)
            initial = None
        except CategoryResult.DoesNotExist:  # new result
            cat_result = CategoryResult(Distribution=dstr, Category=cat)
            # initial = {'Files': list(StudentFile.objects.filter(Type=cat_result.Category.File, Distribution=cat_result.Distribution).distinct())}
        if request.method == "POST":  # submitted form
            if cat_result.Final:
                return render(request, "base.html", context={
                    "Message": "Category Result has already been finalized! Editing is not allowed anymore. "
                               "If this has to be changed, contact support staff"
                })
            if old:
                raise PermissionDenied('Changing history is not allowed.')
            # if files:
            #     category_form = CategoryResultFormFile(request.POST, instance=cat_result, prefix='catform')
            # else:
            category_form = CategoryResultForm(request.POST, instance=cat_result, prefix='catform')
            aspect_forms = []
            for i, aspect in enumerate(cat.aspects.all()):
                try:  # try find existing form
                    aspect_result = CategoryAspectResult.objects.get(CategoryResult=cat_result, CategoryAspect=aspect)
                except CategoryAspectResult.DoesNotExist:  # new clean form
                    aspect_result = CategoryAspectResult(CategoryResult=cat_result, CategoryAspect=aspect)
                aspect_forms.append({
                    "form": AspectResultForm(request.POST, instance=aspect_result, prefix="aspect" + str(i)),
                    "aspect": aspect,
                })
            if category_form.is_valid() and all([form['form'].is_valid() for form in aspect_forms]):
                cat_result = category_form.save()
                # return the form with the cleaned grade, not the one with the (uncleaned) post data:
                # if files:
                #     category_form = CategoryResultFormFile(instance=cat_result, prefix='catform')
                # else:
                category_form = CategoryResultForm(instance=cat_result, prefix='catform')
                for form in aspect_forms:  # these forms do not need to be updated as aspect data is not cleaned.
                    aspect_result = form['form'].instance
                    aspect_result.CategoryResult = cat_result
                    aspect_result.save()
                saved = True
        else:
            # if files:
            #     category_form = CategoryResultFormFile(instance=cat_result, initial=initial, prefix='catform', disabled=cat_result.Final)
            # else:
            category_form = CategoryResultForm(instance=cat_result, prefix='catform', disabled=(cat_result.Final or old))
            aspect_forms = []
            for i, aspect in enumerate(cat.aspects.all()):
                try:
                    aspect_result = CategoryAspectResult.objects.get(CategoryResult=cat_result, CategoryAspect=aspect)
                except CategoryAspectResult.DoesNotExist:
                    aspect_result = CategoryAspectResult(CategoryResult=cat_result, CategoryAspect=aspect)
                aspect_forms.append({
                    "form": AspectResultForm(instance=aspect_result, prefix="aspect" + str(i), disabled=(cat_result.Final or old)),
                    "aspect": aspect,
                })
        return render(request, "results/wizard.html", {
            "step": step,
            "categories": cats,
            "category": cat,
            "categoryform": category_form,
            "aspectsforms": aspect_forms,
            "dstr": dstr,
            "pk": pk,
            "saved": saved,
            "final": cat_result.Final,
            "aspectlabels": CategoryAspectResult.ResultOptions,
            # "files": files,
            'rounding': settings.CATEGORY_GRADE_QUANTIZATION,
            'old': old,
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

    if ts is not None:
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
        'visible': r.Visible if ts is not None else False,
        'form': form if ts is not None else None,
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
                delete_object(aspect)
            delete_object(cat)
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
        tss = get_timeslot()
        if not tss:
            raise PermissionDenied('There is no currently active timeslot to copy to.')
        ts = get_object_or_404(TimeSlot, pk=pk)
        if ts == tss:
            raise PermissionDenied("It is not possible to copy the grades from the current timeslot.")
        if tss.gradecategories.exists():
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
                    old_aspects = cat.aspects.all().defer(None)
                    cat.id = None
                    cat.TimeSlot = get_timeslot()
                    cat.full_clean()
                    cat.save()
                    for aspect in old_aspects:
                        aspect.id = None
                        aspect.Category = cat
                        aspect.full_clean()
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
