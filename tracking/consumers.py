from channels import Group
from channels.auth import channel_session_user_from_http
from django.contrib.auth.decorators import login_required

from proposals.cacheprop import getProp
from .views import getTrack


@channel_session_user_from_http
@login_required
def connectCurrentViewnumber(message, pk):
    track = getTrack(getProp(pk))
    if track.Subject.Status != 4:
        return
    message.channel_session['pk'] = pk
    message.reply_channel.send({'accept' : True})
    Group("viewnumber{}".format(pk)).add(message.reply_channel)
    Group("viewnumber{}".format(pk)).send({'text':str(track.UniqueVisitors.count())})


@channel_session_user_from_http
@login_required
def connectLiveStream(message):
    message.reply_channel.send({'accept' : True})
    Group('livestream').add(message.reply_channel)

'''
@channel_session_user_from_http
@login_required
def disconnectCurrentViewnumber(message):
    pk = message.channel_session['pk']
    Group("viewnumber{}".format(pk)).discard(message.reply_channel)
'''