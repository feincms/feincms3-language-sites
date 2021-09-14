from django.conf import settings
from django.core.checks import Error, register


@register
def check_sites(app_configs, **kwargs):
    if not hasattr(settings, "SITES"):
        return [
            Error(
                "The SITES setting is missing.",
                id="feincms3_language_sites.E001",
            )
        ]

    errors = []

    languages = {code for code, name in settings.LANGUAGES}
    sites = set(settings.SITES)

    if sites_invalid_language_codes := sites - languages:
        errors.append(
            Error(
                f"SITES contains language codes which do not exist in LANGUAGES:"
                f" {', '.join(sorted(sites_invalid_language_codes))}",
                id="feincms3_language_sites.E002",
            )
        )

    if missing_sites := languages - sites:
        errors.append(
            Error(
                f"LANGUAGES contains language codes which do not exist in SITES:"
                f" {', '.join(sorted(missing_sites))}",
                id="feincms3_language_sites.E003",
            )
        )

    return errors
