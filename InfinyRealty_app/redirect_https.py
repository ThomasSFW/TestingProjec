# myapp/middleware/redirect_https.py
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class RedirectToHttpsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure():
            # Build the HTTPS URL
            url = request.build_absolute_uri().replace("http://", "https://")
            return HttpResponsePermanentRedirect(url)

        response = self.get_response(request)
        return response