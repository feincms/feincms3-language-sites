import re
import sys

from django.conf import settings
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
from feincms3 import applications, pages
from feincms3.applications import apps_urlconf, reverse_app
from feincms3.mixins import LanguageAndTranslationOfMixin

import feincms3_language_sites.checks  # noqa


def site_for_host(host):
    for language_code, site in settings.SITES.items():
        site.setdefault("language_code", language_code)
        if "host_re" in site:
            if re.search(site["host_re"], host):
                return site
        elif site["host"] == host:
            return site
    return None


CACHE_KEY = "reverse-language-site-app-cache"
CACHE_TIMEOUT = 60


def apps_urlconfs():
    urlconf_map = cache.get(CACHE_KEY)
    if not urlconf_map or any(
        module for module in urlconf_map.values() if module not in sys.modules
    ):
        fields = ("path", "page_type", "app_namespace", "language_code")
        apps = {code: [] for code, name in settings.LANGUAGES}
        for app in (
            applications._APPS_MODEL._default_manager.filter(is_active=True)
            .with_tree_fields(False)
            .exclude(app_namespace="")
            .values_list(*fields)
            .order_by(*fields)
        ):
            apps[app[-1]].append(app)

        urlconf_map = {
            code: apps_urlconf(apps=site_apps) for code, site_apps in apps.items()
        }
        cache.set(CACHE_KEY, urlconf_map, timeout=CACHE_TIMEOUT)
    return urlconf_map


def reverse_language_site_app(*args, **kwargs):
    language_code = get_language()
    kwargs["urlconf"] = apps_urlconfs()[language_code]
    url = reverse_app(*args, **kwargs, languages=[language_code])
    host = settings.SITES[language_code]["host"]
    return f"//{host}{url}"


class AbstractPageQuerySet(pages.AbstractPageQuerySet):
    def active(self, *, language_code=None):
        return self.filter(
            is_active=True, language_code=language_code or get_language()
        )


class AbstractPage(pages.AbstractPage, LanguageAndTranslationOfMixin):
    # Exactly the same as BasePage.path,
    # except that it is not unique:
    path = models.CharField(
        _("path"),
        max_length=1000,
        blank=True,
        help_text=_("Generated automatically if 'static path' is unset."),
        validators=[
            RegexValidator(
                regex=r"^/(|.+/)$",
                message=_("Path must start and end with a slash (/)."),
            )
        ],
    )

    objects = AbstractPageQuerySet.as_manager(with_tree_fields=True)

    class Meta:
        abstract = True
        ordering = ["position"]
        unique_together = [("language_code", "path")]
        verbose_name = _("page")
        verbose_name_plural = _("pages")

    def _path_clash_candidates(self):
        return super()._path_clash_candidates().filter(language_code=self.language_code)

    def get_absolute_url(self):
        host = settings.SITES[self.language_code]["host"]
        url = super().get_absolute_url()
        return f"//{host}{url}"
