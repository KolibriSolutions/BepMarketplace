#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
"""
General functions, used for mailing
"""

import json
import threading
from math import floor
from smtplib import SMTPException
from time import sleep

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template import loader
from django.utils.html import strip_tags

from index.models import Track
from index.models import UserMeta
from proposals.utils import get_all_proposals, get_share_link
from templates import context_processors


def send_mail(subject, email_template_name, context, to_email):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    # append context processors, some variables from settings
    context = {**context, **context_processors.general()}
    # prepend the marketplace name to the settings
    subject = '{} {}'.format(settings.NAME_PRETTY, subject.strip())
    # generate html email
    html_email = loader.render_to_string(email_template_name, context)
    # attach text and html message
    email_message = EmailMultiAlternatives(subject, strip_tags(html_email), settings.FROM_EMAIL_ADDRESS, [to_email])
    email_message.attach_alternative(html_email, 'text/html')
    # send
    try:
        email_message.send()
    except SMTPException:
        with open("mailcrash.log", "a") as stream:
            stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))
    except ConnectionRefusedError:
        if settings.DEBUG:
            print("Send mail refused!")
        else:
            with open("mailcrash.log", "a") as stream:
                stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))


def mail_project_all(request, project, message=''):
    """
    General function to mail a 'message' to all users responsible or assistant to a given proposal.
    Except the user making the request (-> new behavior 2018).

    :param request: the request of user making the change. This user wil be excluded from mails
    :param project: The proposal that is changed
    :param message: Message string
    :return:
    """
    emails = []
    if project.Status == 1:
        for assistant in project.Assistants.all():
            if (not is_mail_suppressed(assistant)) and request.user != assistant:
                emails.append(assistant.email)
    elif project.Status == 2:  # down/upgrade to 3 is not mailed, only down/upgrade to 2.
        if (not is_mail_suppressed(project.ResponsibleStaff)) and request.user != project.ResponsibleStaff:
            emails.append(project.ResponsibleStaff.email)
    context = {
        'proposal': project,
        'message': message
    }
    for email in emails:
        send_mail("action required for proposal", "email/action_required_email.html", context, email)


def mail_project_single(project, staff, message=''):
    """
    mail a staff member with a given message about a project.

    :param project: The project to mail about
    :param staff: The staff that gets the mail for this project
    :param message: message string
    :return:
    """
    email = staff.email
    context = {
        'proposal': project,
        'message': message,
    }
    send_mail("proposal changed", "email/staff_change_email.html", context, email)


def mail_project_private(project, student, message=''):
    """
    Mail a given student a message about a given proposal. This is only for students with a private proposal.

    :param project: Proposal of this private student
    :param student: the student
    :param message: message string
    :return:
    """
    context = {
        'proposal': project,
        'message': message,
        'sharelink': get_share_link(project.id)
    }
    send_mail("private proposal", "email/private_student_email.html", context, student.email)


def mail_track_heads_pending(stdout=False):
    """
    Mail track heads with their pending proposals. Can be used in an automated script with logging. In that case
     stdout can be set to True.

    :param stdout:
    :return:
    """
    for track in Track.objects.all():
        if stdout:
            print("Track: " + track.Name)
        if track.Head is not None:
            proposals = get_all_proposals().filter(Q(Status=3) & Q(Track=track))
            if proposals.count() > 0:
                e = track.Head.email
                context = {
                    'proposals': proposals,
                    'track': track,
                }
                send_mail("action required for track head", "email/action_required_trackhead_email.html", context, e)
                if stdout:
                    print("Sending proposals: " + str(list(proposals)))
            else:
                if stdout:
                    print("Track has no status 3 pending")
        else:
            if stdout:
                print("Track has no head")


def is_mail_suppressed(user):
    """
    Check if a user has the 'SuppressStatusMails' setting set to True. This is if a user doesn't want to receive mails.

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


class EmailThreadTemplate(threading.Thread):
    """
    Same as email thread but with a template.
    input is array of mails with subject, template and destination
    """

    def __init__(self, mails):
        self.mails = mails
        super().__init__()
        self.channel_layer = get_channel_layer()

    def run(self):
        sleep(1)
        for i, mail in enumerate(self.mails):
            if not mail:
                continue
            if not settings.TESTING:
                async_to_sync(self.channel_layer.group_send)('email_progress',
                                                             {'type': 'update', 'text': json.dumps({
                                                                 'email': mail['email'],
                                                                 'progress': floor(((i + 1) / len(self.mails)) * 100),
                                                             })})
            send_mail(mail['subject'], mail['template'], mail['context'], mail['email'])

# defines for consistency with mastermp
mail_proposal_all = mail_project_all
mail_proposal_single = mail_project_single
mail_proposal_private = mail_project_private
