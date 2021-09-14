from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import override

from feincms3_language_sites.checks import check_sites
from feincms3_language_sites.models import reverse_language_site_app

from .models import Page


def zero_management_form_data(prefix):
    return {
        "%s-TOTAL_FORMS" % prefix: 0,
        "%s-INITIAL_FORMS" % prefix: 0,
        "%s-MIN_NUM_FORMS" % prefix: 0,
        "%s-MAX_NUM_FORMS" % prefix: 1000,
    }


def merge_dicts(*dicts):
    res = {}
    for d in dicts:
        res.update(d)
    return res


class SiteMiddlewareTest(TestCase):
    @override_settings(SITES={"de": {"host": "testserver"}})
    def test_no_404(self):
        page = Page.objects.create(
            title="home",
            slug="home",
            path="/de/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        self.assertContains(self.client.get("/de/"), "home - testapp")
        self.assertEqual(page.get_absolute_url(), "//testserver/de/")

    @override_settings(SITES={"de": {"host": "testserver2"}})
    def test_404(self):
        Page.objects.create(
            title="home",
            slug="home",
            path="/de/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        self.assertEqual(self.client.get("/de/").status_code, 404)


@override_settings(
    MIDDLEWARE=settings.MIDDLEWARE
    + ["feincms3_language_sites.middleware.redirect_to_site_middleware"],
    SITES={
        "de": {
            "host": "de.example.com",
            "host_re": r"de.example.com|testserver",
        },
        "fr": {"host": "fr.example.com"},
    },
)
class RedirectMiddlewareTest(TestCase):
    def test_redirect(self):
        Page.objects.create(
            page_type="standard",
            title="de",
            slug="de",
            language_code="de",
            is_active=True,
        )
        Page.objects.create(
            page_type="standard",
            title="fr",
            slug="fr",
            language_code="fr",
            is_active=True,
        )

        response = self.client.get("/de/", HTTP_HOST="de.example.com")
        self.assertContains(response, "<h1>de</h1>")

        response = self.client.get("/de/", HTTP_HOST="fr.example.com")
        self.assertEqual(response.status_code, 404)

        response = self.client.get("/de/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "http://de.example.com/de/")

        with override_settings(SECURE_SSL_REDIRECT=True):
            response = self.client.get("/de/")
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://de.example.com/de/")

        # self.assertContains(response, "<h1>de</h1>")
        # print(response, response.content.decode("utf-8"))


@override_settings(
    MIDDLEWARE=["feincms3_language_sites.middleware.redirect_to_site_middleware"]
    + settings.MIDDLEWARE,
    SITES={"de": {"host": "de.example.com"}},
)
class WrongOrderRedirectMiddlewareTest(TestCase):
    def test_redirect(self):
        Page.objects.create(
            page_type="standard",
            title="de",
            slug="de",
            language_code="de",
            is_active=True,
        )

        with self.assertRaises(ImproperlyConfigured):
            self.client.get("")


@override_settings(
    SITES={
        "de": {"host": "de.example.com"},
        "fr": {"host": "fr.example.com"},
    },
)
class ReverseAppTest(TestCase):
    def test_reverse_app(self):
        Page.objects.create(
            page_type="application",
            title="de",
            slug="de",
            language_code="de",
            is_active=True,
        )
        Page.objects.create(
            page_type="application",
            title="fr",
            slug="fr",
            language_code="fr",
            is_active=True,
        )

        with override("de"):
            with self.assertNumQueries(1):
                url = reverse_language_site_app("application", "root")
                self.assertEqual(url, "//de.example.com/de/")

            with self.assertNumQueries(0):
                url = reverse_language_site_app("application", "root")
                self.assertEqual(url, "//de.example.com/de/")

        with override("fr"):
            with self.assertNumQueries(1):
                url = reverse_language_site_app("application", "root")
                self.assertEqual(url, "//fr.example.com/fr/")


class ChecksTest(TestCase):
    def assertCheckCodes(self, errors, codes):
        self.assertCountEqual({error.id for error in errors}, codes)

    @override_settings()
    def test_missing(self):
        del settings.SITES

        self.assertCheckCodes(
            check_sites(None),
            {"feincms3_language_sites.E001"},
        )

    @override_settings(
        SITES={"it": {"host": "it.example.com"}},
    )
    def test_mismatch(self):
        self.assertCheckCodes(
            check_sites(None),
            {"feincms3_language_sites.E002", "feincms3_language_sites.E003"},
        )
