import json

import channels
from channels.auth import channel_session_user_from_http, channel_session_user
from django.contrib.auth.decorators import login_required

from BepMarketplace.decorators import group_required
from index.models import User


@channel_session_user_from_http
@login_required
def mailProgress(message):
    """
    Channel to send messages to the mailprogress page. Shows the progress of sending mails.
    
    :param message: 
    :return: 
    """
    message.reply_channel.send({'accept': True})
    channels.Group('emailprogress').add(message.reply_channel)


@channel_session_user_from_http
@group_required("type3staff")
def ECTSConnect(message):
    """
    Connect function for ECTSSubmit
    
    :param message: 
    :return: 
    """
    message.reply_channel.send({'accept': True})
    channels.Group('ectssubmit').add(message.reply_channel)


@channel_session_user
@group_required("type3staff")
def ECTSSubmit(message):
    """
    Receive the form input from the ECTS form, to let support staff supply ECTS of students.

    :param message: 
    :return: 
    """

    data=json.loads(message.content['text'])
    std = data['std']
    ects = data['ects']
    try:
        user = User.objects.get(id=std)
    except:
        channels.Group('ectssubmit').send(
            {'text': '{"type": "alert", "student": "' + str(std) + '", "info":"No such user"}'})
        return

    if user.groups.count() != 0:
        channels.Group('ectssubmit').send(
            {'text': '{"type": "alert", "student": "' + user.username + '", "info":"Not a student!"}'})
        return

    try:
        user.usermeta.ECTS = ects
        user.usermeta.full_clean()
        user.usermeta.save()
    except:
        channels.Group('ectssubmit').send(
            {'text': '{"type": "alert", "student": "' + user.username + '", "info":"ECTS saving failed"}'})
        return

    channels.Group('ectssubmit').send({'text': '{"type": "success", "student": "' + user.username + '", "info": "ECTS: ' + str(user.usermeta.ECTS) + '"}'})


