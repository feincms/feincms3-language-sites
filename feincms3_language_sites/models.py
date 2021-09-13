import re

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _
from feincms3 import mixins, pages


for language_code, site in settings.SITES.items():
    site["language_code"] = language_code
    if "host_re" not in site:
        site["host_re"] = r"^%s$" % re.escape(site["host"])


def site_for_host(host):
    for language_code, site in settings.SITES.items():
        if re.search(site["host_re"], host):
            return site
    return None


class AbstractPageQuerySet(pages.AbstractPageQuerySet):
    def active(self, *, language_code=None):
        return self.filter(
            is_active=True, language_code=language_code or get_language()
        )


class AbstractPage(pages.AbstractPage, mixins.LanguageAndTranslationOfMixin):
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
