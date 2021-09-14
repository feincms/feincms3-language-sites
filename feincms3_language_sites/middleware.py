from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponsePermanentRedirect
from django.utils import translation
from django.utils.cache import patch_vary_headers


def site_middleware(get_response):
    from .models import site_for_host

    def middleware(request):
        request.site = site_for_host(request.get_host())
        if request.site is None:
            raise Http404("No configuration found for %r" % request.get_host())

        translation.activate(request.site["language_code"])
        request.LANGUAGE_CODE = translation.get_language()
        response = get_response(request)
        # Maybe not necessary, but do not take chances.
        patch_vary_headers(response, ("Accept-Language",))
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
        if request.get_host() == request.site["host"] and (
            not settings.SECURE_SSL_REDIRECT or request.is_secure()
        ):
            return get_response(request)

        return HttpResponsePermanentRedirect(
            "http%s://%s%s"
            % (
                "s" if (settings.SECURE_SSL_REDIRECT or request.is_secure()) else "",
                request.site["host"],
                request.get_full_path(),
            )
        )

    return middleware
