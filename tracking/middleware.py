#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import json
from datetime import datetime

from django.utils.deprecation import MiddlewareMixin
from ipware.ip import get_client_ip
from pytz import utc


class TelemetryMiddleware(MiddlewareMixin):
    """
    Middleware to track users activity.
    """

    def WriteLog(self, data):
        type = data.pop('type')
        message = json.dumps(data)
        if type == 'user':
            with open('tracking/telemetry/data/{}.log'.format(data['user']), 'a') as stream:
                stream.write(message + '\n')
        elif type == 'anon_404':
            with open('tracking/telemetry/data/404.log', 'a') as stream:
                stream.write(message + '\n')

    def createpackage(self, request, response):
        return {
            'path': request.path,
            'status_code': response.status_code,
            'ip': get_client_ip(request),
            'method': request.method,
            'timestamp': int(datetime.utcnow().replace(tzinfo=utc).timestamp()),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'referer': request.META.get('HTTP_REFERER')
        }

    def handleanon(self, request, response):
        if response.status_code == 404:
            data = self.createpackage(request, response)
            data['type'] = 'anon_404'
            self.WriteLog(data)

        return response

    def handleuser(self, request, response):
        # if '/js_error_hook/' in request.path:
        #     return response

        data = self.createpackage(request, response)
        data['user'] = request.user.username
        data['type'] = 'user'
        self.WriteLog(data)

        return response

    def process_response(self, request, response):
        """

        :param request:
        :param response:
        :return:
        """
        try:
            try:  # only exists when impersonate is active, crashes if no try except is used
                if request.user.is_impersonate:
                    return response
            except:
                pass

            if request.user.is_superuser:
                return response

            if request.user.is_anonymous:
                return self.handleanon(request, response)
        except:
            # in channels production mode, daphne does not give a user property in request
            # in non daphne a anonymous user object would be given\
            # because of this a try except is necesarry here
            return self.handleanon(request, response)
        return self.handleuser(request, response)
