=======================
feincms3-language-sites
=======================

.. image:: https://github.com/matthiask/feincms3-language-sites/workflows/Tests/badge.svg
    :target: https://github.com/matthiask/feincms3-language-sites/
    :alt: CI Status

Multisite support for `feincms3 <https://feincms3.readthedocs.io>`_.


Usage scenario
==============

Suppose you have a website with several domains and languages but an exact 1:1
mapping between them. Django offers the ``django.contrib.sites`` application to
partition data but you still have to run one webserver per site.

This app offers a feincms3 abstract page model, a middleware and utilities to
support this scenario. Contrary to `feincms3-sites
<https://github.com/matthiask/feincms3-sites>`__ which is even more flexible
and allows arbitrary combinations of languages and domains this app only allows
exactly one domain per language and exactly one language per domain.


Installation
============

* Install the package using ``pip install feincms3-language-sites`` into an
  environment where you're already using feincms3 pages.
* Extend ``feincms3_language_sites.models.AbstractPage`` instead of
  ``feincms3.pages.AbstractPage``. This abstract page already extends
  ``feincms3.mixins.LanguageAndTranslationOfMixin`` so you may remove the
  language mixins (if you have added them before).
* Replace the ``LocaleMiddleware`` with
  ``feincms3_language_sites.middleware.site_middleware``. In case you're using
  feincms3 applications you should ensure that the ``site_middleware`` is added
  before ``feincms3.applications.apps_middleware``.
* Optionally add
  ``feincms3_language_sites.middleware.redirect_to_site_middleware`` if you
  want to enforce the ``host``. The ``SECURE_SSL_REDIRECT`` is also respected.
  The ``redirect_to_site_middleware`` has to be added *before* the
  ``SecurityMiddleware`` otherwise users may get redirected twice in a row.
* Configure the sites.


Configuration
=============

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

Sites are checked in the order they are declared (since dictionaries are
guaranteed to preserve the ordering of keys since Python 3.7).

The keys of the ``SITES`` dictionary have to be equal to all language codes in
``LANGUAGES``. The ``host`` is required and should only consist of the host and
an optional port, nothing else. If ``host_re`` is given the
``request.get_host()`` return value is matched against the ``host_re`` regular
expression, otherwise the ``host`` has to match exactly.

The ``site_middleware`` automatically raises a ``DisallowedHost`` exception if
no site matches the current request (which produces the same error as Django if
the request doesn't match ``ALLOWED_HOSTS``).


Utilities
=========

* ``feincms3_language_sites.models.site_for_host``
* ``feincms3_language_sites.models.reverse_language_site_app``
* ``feincms3_language_sites.templatetags.feincms3_language_sites.site_translations``


Notes
=====

Note that ``Page.objects.active()`` only returns pages in the current language.
If you want to generate translation links (e.g. using ``...|translations`` in a
template) you do not want to use the ``.active()`` queryset method but build
something yourself which runs ``.filter(is_active=True)``.
