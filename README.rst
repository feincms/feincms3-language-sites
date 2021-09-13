=======================
feincms3-language-sites
=======================

.. image:: https://github.com/matthiask/feincms3-language-sites/workflows/Tests/badge.svg
    :target: https://github.com/matthiask/feincms3-language-sites/
    :alt: CI Status

Multisite support for `feincms3 <https://feincms3.readthedocs.io>`_.


* Extend ``feincms3_language_sites.models.AbstractPage`` instead of
  ``feincms3.pages.AbstractPage``
* At (at least) ``feincms3_language_sites.middleware.site_middleware``
* You may now remove the ``LocaleMiddleware``, the ``site_middleware`` is
  sufficient.
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
