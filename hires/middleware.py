from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin
from rest_framework.views import APIView
from rest_framework.response import Response

class CustomCSRFMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Always generate a new CSRF token and set it in cookies
        csrf_token = get_token(request)
        response.set_cookie('csrftoken', csrf_token)
        print(csrf_token,"///////////////")
        return response