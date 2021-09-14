import re

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
from feincms3 import applications, pages
from feincms3.applications import apps_urlconf, reverse_app
from feincms3.mixins import LanguageAndTranslationOfMixin


def site_for_host(host):
    for language_code, site in settings.SITES.items():
        if "host_re" not in site:
            site["host_re"] = r"^%s$" % re.escape(site["host"])
        if "language_code" not in site:
            site["language_code"] = language_code
        if re.search(site["host_re"], host):
            return site
    return None


def reverse_language_site_app(*args, **kwargs):
    fields = ("path", "page_type", "app_namespace", "language_code")
    # TODO maybe cache this. This runs one DB query per invocation
    kwargs["urlconf"] = apps_urlconf(
        apps=applications._APPS_MODEL._default_manager.active()
        .with_tree_fields(False)
        .exclude(app_namespace="")
        .values_list(*fields)
        .order_by(*fields)
    )
    host = settings.SITES[get_language()]["host"]
    url = reverse_app(*args, **kwargs)
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
