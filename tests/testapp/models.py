from content_editor.models import Region, create_plugin_base
from django.utils.translation import gettext_lazy as _
from feincms3 import plugins
from feincms3.applications import PageTypeMixin, TemplateType
from feincms3.mixins import MenuMixin, RedirectMixin

from feincms3_language_sites.models import AbstractPage


class Page(AbstractPage, PageTypeMixin, MenuMixin, RedirectMixin):
    # MenuMixin
    MENUS = [("main", _("main")), ("footer", _("footer"))]

    # PageTypeMixin. We have two templates and four apps.
    TYPES = [
        TemplateType(
            key="standard",
            title=_("standard"),
            template_name="pages/standard.html",
            regions=(Region(key="main", title=_("Main")),),
        ),
        TemplateType(
            key="with-sidebar",
            title=_("with sidebar"),
            template_name="pages/with-sidebar.html",
            regions=(
                Region(key="main", title=_("Main")),
                Region(key="sidebar", title=_("Sidebar")),
            ),
        ),
    ]


PagePlugin = create_plugin_base(Page)


class Snippet(plugins.snippet.Snippet, PagePlugin):
    TEMPLATES = [("snippet.html", _("snippet"))]
