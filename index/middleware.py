from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.utils.deprecation import MiddlewareMixin

from .models import UserAcceptedTerms


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
        user = request.user
        if user.is_superuser or user.is_anonymous or user.is_impersonate:
            # these users do not need to accept terms.
            return
        # urls that should be available if terms are not yet accepted.
        # Allow self, logout and issue #118, promotionfiles on termsaccept.
        if reverse('index:termsaccept') in request.path or \
                '/download/promotionfile/' in request.path or \
                reverse('index:logout') in request.path:
            return

        acceptedusers = cache.get('termsaccepted', [])
        if user.username in acceptedusers:
            # already accepted
            return
        try:
            # user has accepted terms, but was not yet in cache.
            obj = UserAcceptedTerms.objects.get(User=user)
            acceptedusers.append(user.username)
            return
        except UserAcceptedTerms.DoesNotExist:
            # not yet accepted, redirect to index:termsaccept
            pass
        cache.set('termsaccepted', acceptedusers, None)
        return HttpResponseRedirect(reverse('index:termsaccept'))
