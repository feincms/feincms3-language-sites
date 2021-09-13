=======================
feincms3-language-sites
=======================

.. image:: https://github.com/matthiask/feincms3-language-sites/workflows/Tests/badge.svg
    :target: https://github.com/matthiask/feincms3-language-sites/
    :alt: CI Status

Multisite support for `feincms3 <https://feincms3.readthedocs.io>`_.


* Extend ``feincms3_language_sites.models.AbstractPage`` instead of
  ``feincms3.pages.AbstractPage``. This abstract page already extends
  ``feincms3.mixins.LanguageAndTranslationOfMixin`` so you do not have to use
  the mixins adding a language field to the page.
* Replace the ``LocaleMiddleware`` with
  ``feincms3_language_sites.middleware.site_middleware``
* Optionally add
  ``feincms3_language_sites.middleware.redirect_to_site_middleware`` if you
  want to enforce the ``host``. The ``SECURE_SSL_REDIRECT`` is also respected.
  The ``redirect_to_site_middleware`` has to be added *before* the
  ``SecurityMiddleware`` to work correctly.
* Add some configuration for feincms3-language-sites

Possible configuration:

.. code-block:: python

    SITES = {
        "de": {
            "host": "127.0.0.1:8000",
            "host_re": r"example\.com$|127.0.0.1:8000$",
        },
        "fr": {
            "host": "localhost:8000",
        },
    }

Note that ``Page.objects.active()`` only returns pages in the current language.
If you want to generate translation links (e.g. using ``...|translations`` in a
template) you do not want to use the ``.active()`` queryset method but build
something yourself which runs ``.filter(is_active=True)``.
