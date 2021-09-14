from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

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
