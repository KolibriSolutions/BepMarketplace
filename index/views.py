#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from datetime import datetime
from math import floor

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from index.decorators import superuser_required
from general_form import ConfirmForm
from general_mail import send_mail
from support.models import PublicFile
from timeline.utils import get_timephase, get_timephase_number, get_timeslot
from .forms import CloseFeedbackReportForm, FeedbackForm, SettingsForm
from .models import FeedbackReport, Track, UserMeta, Term, UserAcceptedTerms


def index(request):
    """
    The index page, home page, for all users. This displays a simple help string based on the timephase and an
    extensive help text (supplied in the template).

    :param request:
    :return: render of the index page.
    """
    files = PublicFile.objects.filter(TimeSlot=get_timeslot())
    ph = get_timephase_number()
    info = ''
    if request.user.groups.exists():
        if ph <= 2:
            info = "Please use the Proposals menu to create, edit or approve proposals."
        elif ph == 3:
            info = "Students are currently choosing projects. Watch their applications using the applications menu."
        elif ph == 4 or ph == 5:
            info = "The support staff can distribute projects using the support menu. Others will have to wait for the distribution."
        elif ph == 6:
            info = "Students are executing the projects. Watch their files using the Students menu."
        elif ph == 7:
            info = "Students are (almost) presenting their results, watch or edit their grades using the Students menu."
    else:
        if ph <= 2:
            info = ""
        elif ph == 3:
            info = "Use the Proposals menu to view the proposals and to apply. Use the applications menu to manage your applications."
        elif ph == 4:
            info = "Please wait for the support staff to distribute the projects"
        elif ph == 5:
            info = "The projects are distributed, if you have any objections, please contact please contact {support_name} at {contact_email}".format(support_name=settings.SUPPORT_NAME, contact_email=settings.CONTACT_EMAIL)
        elif ph == 6:
            info = "Good luck with your project!"
        elif ph == 7:
            info = "Good luck with your presentation!"
    ts = get_timephase()
    if not ts:
        d = 0
        s = 0
    else:
        # if there is a countdown end take that one, otherwise take the real one
        # take max time of the endday, because the last day is inclusive.
        if ts.CountdownEnd is not None:
            tdelta = datetime.combine(ts.CountdownEnd, datetime.max.time()) - datetime.now()
        else:
            tdelta = datetime.combine(ts.End, datetime.max.time()) - datetime.now()
        if tdelta.total_seconds() < 0:
            d = 0
            s = 0
        else:
            d = tdelta.days
            s = tdelta.seconds
    return render(request, "index/index.html",
                  {"info": info,
                   "files": files,
                   "countdownDays": d,
                   "countdownHours": floor((s / 3600) % 24),
                   "countdownMinutes": floor((s / 60) % 60),
                   'support_role': settings.SUPPORT_ROLE,
                   'support_name': settings.SUPPORT_NAME,
                   'support_email': settings.SUPPORT_EMAIL,
                   }

                  )


def logout(request):
    """
    User logout. This function is still used, also for SAML

    :param request:
    :return:
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    auth_logout(request)
    return render(request, "base.html", {"Message": "You are now logged out. "
                                                    "<a href='/' title='Home'>Go back to the homepage</a>.<br />"
                                                    "To logout of the TU/e single sign on please close your browser."})


@superuser_required()
def list_feedback(request):
    """
    List the feedback supplied via the feedback button. Only for superusers.

    :param request:
    :return:
    """
    return render(request, "index/list_feedback.html", {
        'feedback_list': FeedbackReport.objects.filter(~Q(Status=3))
    })


@login_required
def feedback_form(request):
    """
    The form to give feedback using the feedback button. All users can supply feedback. Superusers can view it.

    :param request:
    :return:
    """
    if request.method != "POST":
        return render(request, "base.html", {
            "Message": "Please do not access this page directly."
        })

    form = FeedbackForm(initial={
        'Url': request.POST['id_Url'],
    })

    return render(request, "index/feedback_form.html", {
        "form": form,
        "formtitle": "Feedback Form",
        "buttontext": "Send",
        'support_name': settings.SUPPORT_NAME,
        "actionlink": "index:feedback_submit"  # redirect to feedback_submit
    })


@login_required
def feedback_submit(request):
    """
    The 'thanks' page after feedback is submitted by a user.
    Also shows form validation errors if present.

    :param request:
    :return:
    """
    if request.method != "POST":
        return render(request, "base.html", {
            "Message": "Please do not access this page directly."
        })
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.Reporter = request.user
        feedback.Status = 1
        feedback.save()
        send_mail("feedback report created", "email/feedback_report_email_created.html", {
            "report": feedback
        }, feedback.Reporter.email)
        send_mail("feedback report created", "email/feedback_report_admin.html", {
            "report": feedback
        }, settings.CONTACT_EMAIL)
        return render(request, "base.html", {
            "Message": "Feedback saved, thank you for taking the time to improve the system!"
        })
    return render(request, "index/feedback_form.html", {
        "form": form,
        "formtitle": "Feedback Form",
        "buttontext": "Send",
        "support_name": settings.SUPPORT_NAME,
    })


@superuser_required()
def feedback_confirm(request, pk):
    """
    Form to confirm the feedback given by a user. Only for superusers. Sends a simple confirm mail to the user.

    :param request:
    :param pk: id of the feedback report
    :return:
    """

    obj = get_object_or_404(FeedbackReport, pk=pk)
    if obj.Status != 1:
        return render(request, "base.html", {
            "Message": "Report is not in open status.",
            "return": "index:list_feedback"
        })
    obj.Status = 2
    obj.save()
    send_mail("feedback report", "email/feedback_report_email_statuschange.html", {
        "report": obj
    }, obj.Reporter.email)

    return render(request, "base.html", {
        "Message": "Report confirmed and reporter notified.",
        "return": "index:list_feedback"
    })


@superuser_required()
def feedback_close(request, pk):
    """
    Close a feedback report. Send a custom message to the user that gave the feedback. Only for superusers

    :param request:
    :param pk: id of the feedback report
    :return:
    """
    obj = get_object_or_404(FeedbackReport, pk=pk)

    if obj.Status == 3:
        return render(request, "base.html", {
            "Message": "Report is already closed.",
            "return": "index:list_feedback"
        })

    if request.method == "POST":
        form = CloseFeedbackReportForm(request.POST, initial={
            'email': obj.Reporter.email
        })
        if form.is_valid():
            obj.Status = 3
            obj.save()
            send_mail("feedback report", "email/feedback_report_email_statuschange.html", {
                "report": obj,
                "message": form.cleaned_data["message"],
            }, obj.Reporter.email)

            return render(request, "base.html", {
                "Message": "Report closed and reporter notified.",
                "return": "index:list_feedback"
            })
    else:
        form = CloseFeedbackReportForm(initial={
            'email': obj.Reporter.email
        })

    return render(request, "GenericForm.html", {
        "formtitle": "Close Feedback Report",
        "buttontext": "Close",
        "form": form
    })


@login_required
def profile(request):
    """
    Displays a profile page for the user.
    For staff members displays the groups that user is in
    For students displays LDAP data and course enrollments (via studyweb).

    :param request:
    :return:
    """
    try:
        meta = request.user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta()
        request.user.usermeta = meta
        meta.save()
        request.user.save()

    tracks = Track.objects.filter(Head=request.user)
    groups = request.user.groups
    if groups.exists() or request.user.is_superuser:
        if groups.filter(name="type2staff").exists():
            type2 = True
        elif groups.filter(name="type2staffunverified").exists():
            type2 = 'Unverified'
        else:
            type2 = False

        vars = {
            "student": False,
            "meta": meta,
            "type1": groups.filter(name="type1staff").exists(),
            "type2": type2,
            "type3": groups.filter(name="type3staff").exists(),
            "type4": groups.filter(name="type4staff").exists(),
            "type5": groups.filter(name="type5staff").exists(),
            "type6": groups.filter(name="type6staff").exists(),
            "SuppressStatusMails": meta.SuppressStatusMails,
        }
        if tracks.count() > 0:
            vars["tracks"] = tracks
    else:
        vars = {
            "student": True,
            "meta": meta,
            "SuppressStatusMails": meta.SuppressStatusMails,
        }
    return render(request, "index/profile.html", vars)


@login_required
def user_settings(request):
    """
    Let a user change its settings, like email preferences.

    :param request:
    :return:
    """
    try:
        meta = request.user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta()
        request.user.usermeta = meta
        meta.save()
        request.user.save()

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            return render(request, "base.html", {
                "Message": 'Settings saved!',
                'return': 'index:profile',
            })
    else:
        form = SettingsForm(instance=meta)

    return render(request, "GenericForm.html", {
        "form": form,
        "formtitle": "Change user settings",
        "buttontext": "Save"
    })


@login_required
def terms_form(request):
    """
    Form for a user to accept the terms of use.

    :param request:
    :return:
    """
    try:
        # already accepted, redirect user to login
        obj = request.user.termsaccepted
        if obj.Stamp <= timezone.now():
            return HttpResponseRedirect('/')
    except UserAcceptedTerms.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            # user accepted terms. Possible already accepted terms in a parallel session, so get_or_create.
            UserAcceptedTerms.objects.get_or_create(User=request.user)
            return HttpResponseRedirect('/')
    else:
        form = ConfirmForm()

    return render(request, 'index/terms.html', {
        'form': form,
        'formtitle': 'I have read and accepted the Terms of Services',
        'buttontext': 'Confirm',
        'terms': Term.objects.all()
    })


def error400(request, exception):
    """
    http 400 page, for instance wrong hostname

    :param request:
    :param exception: needed param by django.
    :return:
    """
    return render(request, "400.html", status=400)


def error403(request, exception):
    """
    http 403 page

    :param request:
    :param exception: Reason why this page is forbidden.
    :return:
    """
    return render(request, "403.html", status=403, context={"exception": exception})


def csrf_failure(request, reason=''):
    """
    http 403 page for CSRF failure

    :param request:
    :param exception: Reason why this page is forbidden.
    :return:
    """
    return render(request, "403_csrf.html", status=403)


def error404(request, exception):
    """
    http 404 page

    :param request:
    :param exception: needed param by django.
    :return:
    """
    return render(request, "base.html", status=404, context={
        "Message": "The page you are looking for does not exist. Please have a look at the <a href=\"/\">homepage</a>"
    })


def error500(request):
    """
    http 500 page

    :param request:
    :return:
    """
    return render(request, "50x.html", status=500)


def about(request):
    """
    About page

    :param request:
    :return:
    """
    return render(request, "index/about.html")
