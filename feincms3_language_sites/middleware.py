from django.conf import settings
from django.core.exceptions import DisallowedHost, ImproperlyConfigured
from django.http import HttpResponsePermanentRedirect
from django.utils import translation


def site_middleware(get_response):
    from .models import site_for_host

    def middleware(request):
        request.site = site_for_host(request.get_host())
        if request.site is None:
            raise DisallowedHost("No configuration found for %r" % request.get_host())

        translation.activate(request.site["language_code"])
        request.LANGUAGE_CODE = translation.get_language()
        response = get_response(request)
        response.setdefault("Content-Language", translation.get_language())
        return response

    return middleware


def redirect_to_site_middleware(get_response):
    def middleware(request):
        if not hasattr(request, "site"):
            raise ImproperlyConfigured(
                'No "site" attribute on request. Insert site_middleware'
                " before redirect_to_site_middleware."
            )

        # Host matches, and either no HTTPS enforcement or already HTTPS
        # Do a redirect if
        # - Host doesn't match
        # - We should be on HTTPS but are not
        if request.get_host() != request.site["host"] or (
            settings.SECURE_SSL_REDIRECT and not request.is_secure()
        ):
            if settings.SECURE_SSL_REDIRECT or request.is_secure():
                protocol = "https"
            else:
                protocol = "http"
            return HttpResponsePermanentRedirect(
                f'{protocol}://{request.site["host"]}{request.get_full_path()}'
            )

        return get_response(request)

    return middleware
