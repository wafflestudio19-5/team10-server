from django.http.response import HttpResponseBadRequest, HttpResponse
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(self, request, provider_id, error, exception, extra_context):
        raise ImmediateHttpResponse(
            'SocialAccount authentication error!',
            'error',
            request,
            #extra_data = {'provider_id': provider_id, 'error': error.__str__(), 'exception': exception.__str__(), 'extra_context': extra_context},
        )
        