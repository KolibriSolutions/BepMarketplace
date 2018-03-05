from datetime import datetime
from math import floor
from urllib import parse

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.http import is_safe_url

from BepMarketplace.decorators import superuser_required, group_required
from general_form import ConfirmForm
from general_mail import send_mail
from support.models import PublicFile
from timeline.utils import get_timephase, get_timephase_number, get_timeslot
from .forms import TrackForm, CloseFeedbackReportForm, FeedbackForm, settingsForm
from .models import FeedbackReport, Track, UserMeta, Term, UserAcceptedTerms


def make_get(get):
    """
    Creates the get string for the login functions, to keep the redirect page after logging in
    An optional get string inside the redirect (usually for storing datatables sort options) is percent-urlencoded

    :param get: a url to encode.
    """
    p = get.find("?")
    if p > 0:
        u = get[0:p - 1]
        g = get[p:]
        return "?next=" + u + "/" + parse.quote_plus(g)
    else:
        u = get
        return "?next=" + u


def gotoNextOrHome(request):
    """
    Used if a get-string is supplied with a "next" argument. This string is used to redirect a user to a page.
    In case a user has to login first, the get string is kept in the url until a successfull login.
    This function processes the request and redirects the user to the 'next' string or otherwise to the homepage

    :param request:
    :return: redirect to a page.
    """
    if 'next' in request.GET.keys():
        # strip leading an trialing "/" to prevent confusion, then re-append a "/"
        get = request.GET["next"].strip('/')
        # strip a possible second get string (for sort order in datatables)
        p = get.find("?")
        g = ''
        if p > 0:
            u = get[0:p-1]
            g = get[p:]
            u += "/"
        else:
            u = get
            g = ''

        #redirect to the next page if the page exists
        #if a link goes to a download, discard it and go to the homepage, as rendering downloads is quite hard
        if u.split("/")[0] == 'download':
            return HttpResponseRedirect('/')
        if is_safe_url(url=u, host=request.get_host()):
            return HttpResponseRedirect("/"+u+g)
        else:
            raise PermissionDenied("This is not allowed. You used an invalid redirect link.")
    # otherwise redirect to home
    return HttpResponseRedirect('/')


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
            info = "The projects are distributed, if you have any objections, please contact Suzanne Kuijlaars."
        elif ph == 6:
            info = "Good luck with your project!"
        elif ph == 7:
            info = "Good luck with your presentation!"
    ts = get_timephase()
    if not ts:
        d=0
        s=0
    else:
        # if there is a countdown end take that one, otherwise take the real one
        if ts.CountdownEnd is not None:
            tdelta = datetime.combine(ts.CountdownEnd, datetime.min.time()) - datetime.now()
        else:
            tdelta = datetime.combine(ts.End, datetime.min.time()) - datetime.now()
        if tdelta.total_seconds()<0:
            d=0
            s=0
        else:
            d=tdelta.days
            s=tdelta.seconds
    return render(request, "index/index.html", {"info" : info, "files": files , "countdownDays":d, "countdownHours":floor((s / 3600) % 24), "countdownMinutes":floor((s / 60) % 60)})


def logout(request):
    """
    User logout. This function is still used, also for SAML

    :param request:
    :return:
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    auth_logout(request)
    return render(request, "base.html", {"Message":"You are now logged out. "
                                                   "<a href='/' title='Home'>Go back to the homepage</a>.<br />"
                                                   "To logout of the TU/e single sign on please close your browser."})


@superuser_required()
def listFeedback(request):
    """
    List the feedback supplied via the feedback button. Only for superusers.

    :param request:
    :return:
    """
    return render(request, "index/ListFeedback.html", {
        'feedback_list': FeedbackReport.objects.filter(~Q(Status=3))
    })


@login_required
def feedbackForm(request):
    """
    The form to give feedback using the feedback button. All users can supply feedback. Superusers can view it.

    :param request:
    :return:
    """
    if request.method != "POST":
        return render(request, "base.html", {
            "Message": "No parameters supplied"
        })

    form = FeedbackForm(initial={
        'Url': request.POST['id_Url'],
    })

    return render(request, "GenericForm.html", {
        "form": form,
        "formtitle": "Feedback Form",
        "buttontext": "Send",
        "actionlink": "index:feedbackSubmit"
    })


@login_required
def feedbackSubmit(request):
    """
    The 'thanks' page after feedback is submitted by a user.

    :param request:
    :return:
    """
    if request.method != "POST":
        return render(request, "base.html", {
            "Message": "No parameters supplied"
        })
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.Reporter = request.user
        feedback.Status = 1
        feedback.save()
        send_mail("email/feedback_report_email_subject.txt", "email/feedback_report_email_created.html", {
            "report": feedback
        }, feedback.Reporter.email,
                  html_email_template_name="email/feedback_report_email_created.html")
        send_mail("New Feedback report created", "email/feedback_report_admin.html", {
            "report" : feedback
        }, settings.CONTACT_EMAIL, html_email_template_name="email/feedback_report_admin.html")
        return render(request, "base.html", {
            "Message": "Feedback saved, thank you for taking the time to improve the system!"
        })
    return render(request, "GenericForm.html", {
        "form": form
    })


@superuser_required()
def feedbackConfirm(request, pk):
    """
    Form to confirm the feedback given by a user. Only for superusers. Sends a simple confirm mail to the user.

    :param request:
    :param pk: id of the feedback report
    :return:
    """

    obj = get_object_or_404(FeedbackReport, pk=pk)
    if obj.Status != 1:
        return render(request, "base.html", {
            "Message": "Report not in open status",
            "return": "index:feedbacklist"
        })
    obj.Status = 2
    obj.save()
    send_mail("email/feedback_report_email_subject.txt", "email/feedback_report_email_statuschange.html", {
        "report": obj
    }, obj.Reporter.email,
              html_email_template_name="email/feedback_report_email_statuschange.html")

    return render(request, "base.html", {
        "Message": "Report confirmed and reporter notified",
        "return": "index:feedbacklist"
    })


@superuser_required()
def feedbackClose(request, pk):
    """
    Close a feedback report. Send a custom message to the user that gave the feedback. Only for superusers

    :param request:
    :param pk: id of the feedback report
    :return:
    """
    obj = get_object_or_404(FeedbackReport, pk=pk)

    if obj.Status == 3:
        return render(request, "base.html", {
            "Message": "Report already closed",
            "return": "index:feedbacklist"
        })

    if request.method == "POST":
        form = CloseFeedbackReportForm(request.POST, initial={
            'email': obj.Reporter.email
        })
        if form.is_valid():
            obj.Status = 3
            obj.save()
            send_mail("email/feedback_report_email_subject.txt", "email/feedback_report_email_statuschange.html", {
                "report": obj,
                "message": form.cleaned_data["message"],
            }, obj.Reporter.email,
                      html_email_template_name="email/feedback_report_email_statuschange.html")

            return render(request, "base.html", {
                "Message": "Report closed and reporter notified",
                "return": "index:feedbacklist"
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
    if groups.exists():
        if groups.filter(name="type2staff").exists():
            type2 = True
        elif groups.filter(name="type2staffunverified").exists():
            type2 = 'Unverified'
        else:
            type2 = False

        pvars = {
            "student": False,
            "type1": groups.filter(name="type1staff").exists(),
            "type2": type2,
            "type3": groups.filter(name="type3staff").exists(),
            "type4": groups.filter(name="type4staff").exists(),
            "type5": groups.filter(name="type5staff").exists(),
            "type6": groups.filter(name="type6staff").exists(),
            "SuppressStatusMails": meta.SuppressStatusMails,
        }
        if tracks.count() > 0:
            pvars["tracks"] = tracks
    else:
        pvars = {
            "student": True,
            "meta": meta,
            "SuppressStatusMails": meta.SuppressStatusMails,
        }
    return render(request, "index/profile.html", pvars)


@login_required
def changeSettings(request):
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
        form = settingsForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            return render(request, "base.html", {
                "Message": 'Settings saved!',
                'return': 'index:profile',
            })
    else:
        form = settingsForm(instance=meta)

    return render(request, "GenericForm.html", {
        "form": form,
        "formtitle": "Change user settings",
        "buttontext": "Save"
    })


@login_required
def termsform(request):
    """
    Form for a user to accept the terms of use.

    :param request:
    :return:
    """
    try:
        obj = request.user.termsaccepted
        if obj.Stamp <= datetime.now():
            return HttpResponseRedirect('/')
    except:
        pass

    if request.method == 'POST':
        form = ConfirmForm(request.POST)
        if form.is_valid():
            obj = UserAcceptedTerms(User=request.user)
            obj.save()
            return HttpResponseRedirect('/')
    else:
        form = ConfirmForm()

    return render(request, 'index/Terms.html', {
        'form' : form,
        'formtitle' : 'I have read and accepted the Terms of Services',
        'buttontext' : 'Confirm',
        'terms' : Term.objects.all()
    })


@group_required('type3staff')
def edit_tracks(request):
    """
    Edit all tracks.

    :param request:
    :param pk: pk of the proposal to edit file of
    :param ty: type of file to edit, either i for image or a for attachement
    :return:
    """
    formSet = modelformset_factory(Track, form=TrackForm, can_delete=False)
    formset = formSet(queryset=Track.objects.all())

    if request.method == 'POST':
        formset = formSet(request.POST)
        if formset.is_valid():
            formset.save()
            return render(request, "base.html",
                          {"Message": "Track changes saved!"})
    return render(request, 'GenericForm.html',
                  {'formset': formset, 'formtitle': 'Track Head edit',
                   'buttontext': 'Save changes'})


def error400(request):
    """
    http 400 page, for instance wrong hostname

    :param request:
    :return:
    """
    return render(request, "400.html", status=400)


def error404(request):
    """
    http 404 page

    :param request:
    :return:
    """
    return render(request, "base.html", status=404, context={
        "Message": "The page you are looking for does not exist. Please have a look at the <a href=\"/\">homepage</a>"
    })


def error403(request, exception):
    """
    http 403 page

    :param request:
    :param exception: Reason why this page is forbidden.
    :return:
    """
    return render(request, "403.html", status=403, context={"exception": exception})


def error500(request):
    """
    http 500 page

    :param request:
    :return:
    """
    return render(request, "50x.html", status=500, context={
        "reason": "Something went wrong in the server. The BEP marketplace team has been automatically notified. </br>"
                    "Please help them by sending an email to <a href=\"mailto:bepmarketplace@tue.nl?subject=BugReport\">bepmarketplace@tue.nl</a> with more information what you were trying to do. <br/>"
                    "Thanks in advance!"
    })


def about(request):
    """
    About page

    :param request:
    :return:
    """
    return render(request, "index/about.html")
