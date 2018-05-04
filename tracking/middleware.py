import json
from datetime import datetime
from pytz import utc
from django.utils.deprecation import MiddlewareMixin
from ipware.ip import get_real_ip
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class TelemetryMiddleware(MiddlewareMixin):
    """
    Middleware to track users activity.
    It sends the users information to a seperate systemd service to log the data.
    """

    def createpackage(self, request, response):
        return {
            'path'          : request.path,
            'status_code'   : response.status_code,
            'ip'            : get_real_ip(request),
            'method'        : request.method,
            'timestamp'     : int(datetime.utcnow().replace(tzinfo=utc).timestamp()),
            'user_agent'    : request.META.get('HTTP_USER_AGENT')
        }

    def handleanon(self, request, response):
        if response.status_code == 404:
            data = self.createpackage(request, response)
            data['type'] = 'anon_404'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('telemetry', {"type": 'update', 'text': json.dumps(data)})

        return response

    def handleuser(self, request, response):
        data = self.createpackage(request, response)
        data['user'] = request.user.username
        data['type'] = 'user'

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('telemetry', {"type": 'update', 'text': json.dumps(data)})
        data.pop('user_agent', None)
        data['timestamp'] = datetime.now().strftime("%H:%M:%S")
        async_to_sync(channel_layer.group_send)('live_{}'.format(request.user.username),
                                                {"type": 'update', 'text': json.dumps(data)})
        async_to_sync(channel_layer.group_send)('liveview_telemetry', {"type": 'update', 'text': json.dumps(data)})
        return response

    def process_response(self, request, response):

        """

        :param request:
        :param response:
        :return:
        """
        try:
            try:#only exists when impersonate is active, crashes if no try except is used
                if request.user.is_impersonate:
                    return response
            except:
                pass

            if request.user.is_superuser:
                return response

            if request.user.is_anonymous:
                return self.handleanon(request, response)
        except:
            #in channels production mode, daphne does not give a user property in request
            # in non daphne a anonymous user object would be given\
            # because of this a try except is necesarry here
            return self.handleanon(request, response)
        return self.handleuser(request, response)