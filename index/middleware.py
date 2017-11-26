from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from .models import UserAcceptedTerms
from django.http import HttpResponseRedirect
from django.shortcuts import reverse

class TermsMiddleware(MiddlewareMixin):
    """
    Middleware to check if the user has accepted the terms of use.
    Shows index:termsaccept if the terms are not yet accepted.
    """
    def process_request(self, request):
        """

        :param request:
        :return:
        """
        try:
            user = request.user
        except:
            return

        try:#only exists when impersonate is active, crashes if no try except is used
            if user.is_impersonate:
                return
            if user.is_superuser or user.is_anonymous:
                return
        except:
            pass

        if reverse('index:termsaccept') in request.path:
            return

        acceptedusers = cache.get('termsaccepted', [])

        if user.username in acceptedusers:
            return
        try:
            obj = UserAcceptedTerms.objects.get(User=user)
            acceptedusers.append(user.username)
            return
        except UserAcceptedTerms.DoesNotExist:
            pass

        cache.set('termsaccepted', acceptedusers, None)
        return HttpResponseRedirect(reverse('index:termsaccept'))