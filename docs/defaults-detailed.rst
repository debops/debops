.. _nginx__ref_default_variable_details:

Default variable details
========================

Some of ``debops.nginx`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _nginx__ref_servers:

Nginx servers
-------------

.. warning: This section is currently incomplete. The options need to be
   converted from `templates/etc/nginx/sites-available/default.conf.j2`.

.. _nginx__ref_http_xss_protection:

``xss_protection``
  Optional, string. Value of the ``X-XSS-Protection`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to :envvar:`nginx__http_xss_protection`.

  ``1``
    Browsers should enable there build in cross-site scripting protection.

  ``mode=block``
    In case a cross-site scripting attack is detected, block the page from rendering.

    Note that the this option might create
    `a vulnerability in old versions of Internet Explorer
    <https://github.com/helmetjs/helmet#xss-filter-xssfilter>`.

  For more details and discussion see `What is the http-header
  “X-XSS-Protection”?
  <https://stackoverflow.com/questions/9090577/what-is-the-http-header-x-xss-protection>`_.

.. _nginx__ref_permitted_cross_domain_policies:

``permitted_cross_domain_policies``
  Optional, string. Value of the ``X-Permitted-Cross-Domain-Policies`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to
  :envvar:`nginx__http_permitted_cross_domain_policies`.

  Should cross domain policies be permitted?

.. _nginx__ref_http_robots_tag:

``robots_tag``
  Optional, list of strings or string. Value of the ``X-Robots-Tag`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to
  :envvar:`nginx__http_robots_tag`.

  This allows you to give search engine bots hints how they should handle the
  website. For example, when you don’t want that search engines don’t "index"
  your website, you can set this variable to ``none``.

  .. note:: This header field is merely a hint for the search engine bot,
     nothing more and they might ignore it. For example, Google sets this
     straight in their first sentence in the documentation which says "This
     document details how the page-level indexing settings allow you to control
     how Google `makes content available through search results`."
     So you will need to prevent the search engine bots from crawling the site
     in the first place in case you want to prevent that.

  Refer to `robots meta tag and X-Robots-Tag HTTP header specifications
  <https://developers.google.com/webmasters/control-crawl-index/docs/robots_meta_tag>`_
  for more details.

``welcome``
  Optional, boolean. Defaults to ``False``.
  If ``True`` a welcome page is generated.

``welcome_force``
  Optional, boolean.
  Ensure that the templated file is up-to-date if ``True``.
  Set to ``False`` by default to ensure idempotent operation.
