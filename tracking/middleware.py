import channels
import json
from datetime import datetime
from pytz import utc
from django.utils.deprecation import MiddlewareMixin
from ipware.ip import get_real_ip

class TelemetryMiddleware(MiddlewareMixin):
    """
    Middleware to track users activity.
    It sends the users information to a seperate systemd service to log the data.
    """
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

            if request.user.is_superuser or request.user.is_anonymous:
                return response

        except:
            #in channels production mode, daphne does not give a user property in request
            # in non daphne a anonymous user object would be given\
            # because of this a try except is necesarry here
            return response
        channels.Group('telemetry').send({'text' : json.dumps({
            'path'          : request.path,
            'status_code'   : response.status_code,
            'ip'            : get_real_ip(request),
            'method'        : request.method,
            'user'          : request.user.username,
            'timestamp'     : int(datetime.utcnow().replace(tzinfo=utc).timestamp()),
            'user_agent'    : request.META.get('HTTP_USER_AGENT')
        })})

        return response