"""
General functions, used for mailing
"""
import json
import threading
from math import floor
from time import sleep

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template import loader
from django.utils.html import strip_tags

from proposals.utils import get_all_proposals, get_share_link
from index.models import Track
from index.models import UserMeta


def send_mail(subject_template_name, email_template_name,
              context, to_email, html_email_template_name=None):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    if ".txt" in subject_template_name:
        subject = loader.render_to_string(subject_template_name, context)
    else:
        subject = subject_template_name

    from_email = settings.FROM_EMAIL_ADDRESS
    context['email'] = settings.CONTACT_EMAIL
    context['domain'] = settings.DOMAIN
    context['name'] = settings.NAME_PRETTY
    context['toemail'] = to_email
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, strip_tags(body), from_email, [to_email])
    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')
    try:
        email_message.send()
    except:
        with open("mailcrash.log", "a") as stream:
            if html_email_template_name is not None:
                stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))
            else:
                stream.write("Mail to {} could not be send:\n{}\n".format(to_email, body))


def isMailSuppressed(user):
    """
    Check if a user has the 'suppresstatusmails' setting set to True. This is if a user doesn't want to receive mails.

    :param user:
    :return:
    """
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta()
        user.usermeta = meta
        meta.save()
        user.save()
    return meta.SuppressStatusMails


def mailAffectedUser(request, proposal, message=''):
    """
    General function to mail a 'message' to all users responsible or assistant to a given proposal.

    :param request:
    :param proposal: The proposal that is changed
    :param message: Message string
    :return:
x    """
    emails = []
    if proposal.Status == 1:
        for assistant in proposal.Assistants.all():
            if not isMailSuppressed(assistant):
                emails.append(assistant.email)
    elif proposal.Status == 2:
        if not isMailSuppressed(proposal.ResponsibleStaff):
            emails.append(proposal.ResponsibleStaff.email)

    current_site = get_current_site(request)
    domain = current_site.domain
    context = {
        'domain': domain,
        'proposal': proposal,
        'message': message
    }
    for e in emails:
        send_mail("email/action_required_email_subject.txt", "email/action_required_email.html", context,
              e, html_email_template_name="email/action_required_email.html")


def mailPrivateStudent(request, proposal, student, message=''):
    """
    Mail a given student a message about a given proposal. This is only for students with a private proposal.

    :param request:
    :param proposal: Proposal of this private student
    :param student: the student
    :param message: message string
    :return:
    """
    email = student.email
    current_site = get_current_site(request)
    domain = current_site.domain
    context = {
        'domain'    : domain,
        'proposal'  : proposal,
        'message'   : message,
        'sharelink' : get_share_link(request, proposal.id)
    }
    send_mail("email/private_student_mail_subject.txt", "email/private_student_email.html", context,
              email,
              html_email_template_name="email/private_student_email.html")


def mail_proposal_single(request, proposal, staff, message=''):
    """
    mail a staff member with a given message about a project.

    :param request:
    :param proposal: The proposal to mail about
    :param staff: The staff that gets the mail for this project
    :param message: message string
    :return:
    """
    email = staff.email
    context = {
        'proposal'  : proposal,
        'message'   : message,
    }
    send_mail("email/staff_change_mail_subject.txt", "email/staff_change_email.html", context,
              email, html_email_template_name="email/staff_change_email.html")


class EmailThreadMultipleTemplate(threading.Thread):
    """
    Same as emailthread but with a template.
    """
    def __init__(self, mails):
        self.mails = mails
        super().__init__()
        self.channel_layer = get_channel_layer()

    def run(self):
        """

        """
        sleep(5)
        for i, mail in enumerate(self.mails):
            if mail is None or mail == '':
                continue
            package = {
                'email' : mail['email'],
                'progress' : floor(((i+1)/len(self.mails))*100),
            }
            # channels.Group('emailprogress').send({'text':json.dumps(package)})
            async_to_sync(self.channel_layer.group_send)('emailprogress', {"type": 'update', 'text': json.dumps(package)})
            send_mail(mail['subject'], mail['template'], mail['context'],
                      mail['email'], html_email_template_name=mail['template'])


class EmailThread(threading.Thread):
    """
    Send a lot of mails with delay in between. Show a progress bar page for status.
    """
    def __init__(self, subject, message, context, emails):
        self.subject = subject
        self.message = message
        self.context = context
        self.emails = emails
        super().__init__()
        self.channel_layer = get_channel_layer()

    def run(self):
        """

        """
        sleep(5)
        for i, email in enumerate(self.emails):
            if email is None or email == '':
                continue
            package = {
                'email' : email,
                'progress' : floor(((i+1)/len(self.emails))*100),
            }
            # channels.Group('emailprogress').send({'text':json.dumps(package)})
            async_to_sync(self.channel_layer.group_send)('emailprogress', {"type": 'update', 'text': json.dumps(package)})
            send_mail(self.subject, self.message, self.context,
                      email, html_email_template_name=self.message)


def MailTrackHeadsPending(stdout=False):
    """
    Mail track heads with their pending proposals. Can be used in an automated script with logging. In that case
     stdout can be set to True.

    :param stdout:
    :return:
    """
    for track in Track.objects.all():
        if stdout:
            print("Track: "+track.Name)
        if track.Head is not None:
            proposals = get_all_proposals().filter(Q(Status=3) & Q(Track=track))
            if proposals.count() > 0:
                e = track.Head.email
                context = {
                    'domain': settings.DOMAIN,
                    'proposals': proposals,
                    'Track': track,
                }
                send_mail("email/action_required_trackhead_email_subject.txt", "email/action_required_trackhead_email.html", context,
                      e, html_email_template_name="email/action_required_trackhead_email.html")
                if stdout:
                    print("Sending proposals: "+str(list(proposals)))
            else:
                if stdout:
                    print("Track has no status 3 pending")
        else:
            if stdout:
                print("Track has no head")
