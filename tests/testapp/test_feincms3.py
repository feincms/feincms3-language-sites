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


@override_settings(
    MIDDLEWARE=settings.MIDDLEWARE
    + ["feincms3_language_sites.middleware.site_middleware"],
)
class SiteMiddlewareTest(TestCase):
    @override_settings(SITES={"de": {"host": "testserver"}})
    def test_no_404(self):
        Page.objects.create(
            title="home",
            slug="home",
            path="/de/",
            static_path=True,
            language_code="de",
            is_active=True,
        )
        self.assertContains(self.client.get("/de/"), "home - testapp")

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
