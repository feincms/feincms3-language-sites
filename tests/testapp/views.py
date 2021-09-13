from django.shortcuts import get_object_or_404, render
from feincms3.regions import Regions
from feincms3.renderer import TemplatePluginRenderer

from .models import Page, Snippet


renderer = TemplatePluginRenderer()
renderer.register_template_renderer(
    Snippet,
    lambda plugin: plugin.template_name,
    lambda plugin, context: {"additional": "context"},
)


def page_detail(request, path=None):
    page = get_object_or_404(
        Page.objects.active(), path=("/%s/" % path) if path else "/"
    )
    page.activate_language(request)

    return render(
        request,
        page.type.template_name,
        {
            "page": page,
            "regions": Regions.from_item(
                page, renderer=renderer, inherit_from=page.ancestors().reverse()
            ),
        },
    )
