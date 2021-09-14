from content_editor.models import Region, create_plugin_base
from django.utils.translation import gettext_lazy as _
from feincms3 import plugins
from feincms3.applications import ApplicationType, PageTypeMixin, TemplateType

from feincms3_language_sites.models import AbstractPage


class Page(AbstractPage, PageTypeMixin):
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
        ApplicationType(
            key="application",
            title=_("application"),
            urlconf="testapp.application_urls",
        ),
    ]


PagePlugin = create_plugin_base(Page)


class Snippet(plugins.snippet.Snippet, PagePlugin):
    TEMPLATES = [("snippet.html", _("snippet"))]
