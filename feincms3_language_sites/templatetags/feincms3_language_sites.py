from django import template
from django.conf import settings
from feincms3.templatetags.feincms3 import translations


register = template.Library()


@register.filter
def site_translations(page):
    # Cannot use page.translations().active() because .active() will always
    # filter out pages from other sites.
    try:
        pages = page.translations().filter(is_active=True)
    except (AttributeError, TypeError):
        pages = None
    return [
        {
            **item,
            "site": settings.SITES[item["code"]],
            "site_link": "//" + settings.SITES[item["code"]]["host"],
        }
        for item in translations(pages)
    ]
