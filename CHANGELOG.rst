==========
Change log
==========

Next version
~~~~~~~~~~~~

0.3 (2023-11-01)
~~~~~~~~~~~~~~~~

- Fixed the applications clash check.
- Dropped compatibility with Python 3.8 since we're requiring ``feincms3>=4.5``
  now which only supports Python 3.9 or better.


0.2 (2023-09-07)
~~~~~~~~~~~~~~~~

- Stopped ``redirect_to_site_middleware`` from using permanent redirects if
  ``DEBUG`` is ``True``.


0.1 (2023-07-07)
~~~~~~~~~~~~~~~~

- Started writing a CHANGELOG.
- Removed the contextvars/contextlib helpers; Django already tracks the
  currently active language for us, that should be sufficient.
- Increased the test coverage.
- Added checks for the presence and correctness of the ``SITES`` setting.
- Added Python 3.10, 3.11, Django 4.1, 4.2 to the CI.
- Changed the code to raise a ``DisallowedHost`` exception instead of a 404 if
  unable to find a matching host for the current request.
- Switched to pre-commit.
- Fixed a bug where the ``redirect_to_site_middleware`` would redirect too
  often.
- Added a ``AbstractPage.site`` property returning the site for the page's
  language.
- Added an additional ``unique_together`` constraint for the
  ``LanguageAndTranslationOfMixin``.
- Added a template filter for easily generating links to translated content on
  other sites.
- Fixed a crash which happened when the database contained apps in languages
  which have been removed from the ``LANGUAGES`` setting in the meantime.
- Stopped producing protocol-relative URLs, rely on the ``SECURE_SSL_REDIRECT``
  setting instead.


`0.0.1`_ (2021-09-14)
~~~~~~~~~~~~~~~~~~~~~

- Initial public version.

.. _0.0.1: https://github.com/matthiask/feincms3-language-sites/commit/7a63ed5bf
