from channels import Group
from channels.auth import channel_session_user_from_http
from django.contrib.auth.decorators import login_required
from .models import TelemetryKey

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

def connectTelemetry(message, key):
    if len(key) != 64:
        message.reply_channel.send({'accept': False})
        return

    try:
        obj = TelemetryKey.objects.get(Key=key)
    except TelemetryKey.DoesNotExist:
        message.reply_channel.send({'accept' : False})
        return

    if not obj.is_valid():
        message.reply_channel.send({'accept' : False})
        return

    message.reply_channel.send({'accept': True})
    Group('telemetry').add(message.reply_channel)