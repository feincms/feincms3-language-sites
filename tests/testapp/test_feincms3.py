from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase
from django.test.utils import isolate_apps, override_settings
from django.urls import NoReverseMatch
from django.utils.translation import override

from feincms3_language_sites.checks import check_sites
from feincms3_language_sites.models import (
    CACHE_KEY,
    AbstractPage,
    apps_urlconfs,
    cache,
    reverse_language_site_app,
)
from feincms3_language_sites.templatetags.feincms3_language_sites import (
    site_translations,
)
from testapp.models import Page


class SiteMiddlewareTest(TestCase):
    @override_settings(SITES={"de": {"host": "testserver"}})
    def test_no_400(self):
        page = Page.objects.create(
            title="home",
            slug="home",
            path="/de/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        self.assertContains(self.client.get("/de/"), "home - testapp")
        self.assertEqual(page.get_absolute_url(), "http://testserver/de/")

    @override_settings(SITES={"de": {"host": "testserver2"}})
    def test_400(self):
        Page.objects.create(
            title="home",
            slug="home",
            path="/de/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        self.assertEqual(self.client.get("/de/").status_code, 400)


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

        with override_settings(DEBUG=True):
            response = self.client.get("/de/")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response["Location"], "http://de.example.com/de/")

        with override_settings(SECURE_SSL_REDIRECT=True):
            response = self.client.get("/de/", secure=False)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://de.example.com/de/")

            response = self.client.get("/de/", secure=True)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://de.example.com/de/")

            response = self.client.get("/de/", HTTP_HOST="de.example.com", secure=False)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://de.example.com/de/")

            response = self.client.get("/de/", HTTP_HOST="de.example.com", secure=True)
            self.assertEqual(response.status_code, 200)

        with override_settings(SECURE_SSL_REDIRECT=False):
            response = self.client.get("/de/", secure=False)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "http://de.example.com/de/")

            response = self.client.get("/de/", secure=True)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response["Location"], "https://de.example.com/de/")

            response = self.client.get("/de/", HTTP_HOST="de.example.com", secure=False)
            self.assertEqual(response.status_code, 200)

            response = self.client.get("/de/", HTTP_HOST="de.example.com", secure=True)
            self.assertEqual(response.status_code, 200)

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
        "en": {"host": "en.example.com"},
        "de": {"host": "de.example.com"},
        "fr": {"host": "fr.example.com"},
    },
)
class ReverseAppTest(TestCase):
    def setUp(self):
        cache.delete(CACHE_KEY)

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

        with self.assertNumQueries(1):
            urlconf_map = apps_urlconfs()
        self.assertEqual(
            urlconf_map,
            {
                "en": "testapp.urls",
                "de": "urlconf_fd5a0537769ae95be140eeccf96b8d39",
                "fr": "urlconf_5a381ea1f57c9d934cf1fac7c23956c0",
            },
        )

        with self.assertNumQueries(0):
            with override("de"):
                url = reverse_language_site_app("application", "root")
                self.assertEqual(url, "http://de.example.com/de/")

                url = reverse_language_site_app("does-not-exist", "view", fallback="/")
                self.assertEqual(url, "http://de.example.com/")

            with override("fr"):
                url = reverse_language_site_app("application", "root")
                self.assertEqual(url, "http://fr.example.com/fr/")

            with override("en"), self.assertRaises(NoReverseMatch):
                reverse_language_site_app("application", "root")

    def test_invalid_language(self):
        # "it" doesn't exist in LANGUAGES
        Page.objects.create(
            page_type="application",
            title="it",
            slug="it",
            language_code="it",
            is_active=True,
        )
        self.assertEqual(
            apps_urlconfs(),
            {"en": "testapp.urls", "de": "testapp.urls", "fr": "testapp.urls"},
        )


class ChecksTest(TestCase):
    def assertCheckCodes(self, errors, codes):  # noqa: N802
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


@override_settings(
    SITES={
        "en": {"host": "en.example.com"},
        "de": {"host": "de.example.com"},
        "fr": {"host": "fr.example.com"},
    },
)
class PagesModelTest(TestCase):
    def test_validation(self):
        page_de = Page.objects.create(
            title="home",
            slug="home",
            path="/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        page_en = Page.objects.create(
            title="home",
            slug="home",
            path="/",
            static_path=True,
            language_code="en",
            is_active=True,
        )

        # Doesn't raise
        page_de.full_clean()
        page_en.full_clean()

        with self.assertRaises(ValidationError):
            page_en.language_code = "de"
            page_en.full_clean()

    def test_site_translations_filter(self):
        page_en = Page.objects.create(
            title="home",
            slug="home",
            path="/home/",
            static_path=True,
            language_code="en",
            is_active=True,
        )
        page_de = Page.objects.create(
            title="start",
            slug="start",
            path="/start/",
            static_path=True,
            language_code="de",
            is_active=True,
            translation_of=page_en,
        )

        self.assertEqual(
            site_translations(page_de),
            [
                {
                    "code": "en",
                    "name": "English",
                    "object": page_en,
                    "site": {"host": "en.example.com"},
                    "site_link": "//en.example.com",
                },
                {
                    "code": "de",
                    "name": "German",
                    "object": page_de,
                    "site": {"host": "de.example.com"},
                    "site_link": "//de.example.com",
                },
                {
                    "code": "fr",
                    "name": "French",
                    "object": None,
                    "site": {"host": "fr.example.com"},
                    "site_link": "//fr.example.com",
                },
            ],
        )

        self.assertEqual(
            [lang["code"] for lang in site_translations(None)],
            ["en", "de", "fr"],
        )
        self.assertEqual(
            [lang["code"] for lang in site_translations("page")],
            ["en", "de", "fr"],
        )

    @isolate_apps("testapp")
    def test_page_with_missing_unique_together(self):
        """Page subclass without unique_together fails validation"""

        class Page(AbstractPage):
            class Meta:
                pass

        errors = Page.check()
        error_ids = [error.id for error in errors]
        self.assertIn("feincms3_language_sites.E001", error_ids)
