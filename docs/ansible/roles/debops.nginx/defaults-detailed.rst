.. _nginx__ref_default_variable_details:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.nginx`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. This section is intended to be similar to the docs in debops.apache. If you
   modify this section, consider also checking debops.apache if the same also
   applies there, please.

.. contents::
   :local:
   :depth: 2


.. _nginx__ref_servers:

nginx__servers
--------------

Common role options
~~~~~~~~~~~~~~~~~~~

``name``
  Required, string or list of strings.
  Domain names for the `Nginx server_name option documentation`_.

  The first element is used to create the name of the nginx configuration
  file and must be a normal domain name, other elements can include
  wildcards and regexp matches.

  The list can also be empty (but needs to be defined) in which case the
  configuration it is included in will be named :file:`default`.

``filename``
  Optional, string.
  Alternative name of the nginx configuration file under the
  :file:`/etc/nginx/sites-available/` directory. The suffix :file:`.conf` will be
  added automatically. This can be used to distinguish different server
  configurations for the same ``item.name``. For example separate
  configuration for HTTP and HTTPS.

``hostname``
  Optional. String or a list of hostnames or subdomain names without dots. If
  it's defined, the role will generate ``server { }`` blocks that support
  redirecting the short hostnames or subdomains in the ``*.local`` domain
  managed by Avahi/mDNS to their corresponding FQDNs. For example:

  - ``host/`` -> ``host.example.com``
  - ``host.local`` -> ``host.example.com``

  The ``example.com`` domain will be based on the ``hostname_domain``
  parameter, or if not specified on the first value of the ``name`` parameter.
  Users can use the short hostnames in browsers by appending ``/`` character
  after the short name. Specifying directories or arguments is also supported.

  This allows the :command:`nginx` webserver to correctly handle short
  subdomains passed to it via DNS suffixes defined in :file:`/etc/resolv.conf`,
  or subdomains reachable via Avahi ``*.local`` domain.

  If the ``hostname`` parameter is not specified, the role will automatically
  generate subdomains based on the value of the ``name`` parameter; only
  alphanumeric subdomains with optional dashes and underscores are supported in
  this mode. To tell the role to not autogenerate the redirection, set the
  ``hostname`` parameter to ``False``.

``hostname_domain``
  Optional. Specify the base DNS domain to use for short hostnames and
  subdomains. You can use this to set the base domain in multi-subdomain
  environments. For example, setting it to ``example.com`` will result in
  redirects:

  - ``host/`` -> ``host.example.com``
  - ``sub.host/`` -> ``sub.host.example.com``

  Supporting more than one level of subdomains with DNS suffixes on the clients
  depends on the :man:`resolv.conf(5)` configuration, the ``ndots`` parameter.

  If this parameter is not specified, the role will check the list in the
  :envvar:`nginx__hostname_domains` for possible domain suffixes and use the
  first one found there that matches the current server subdomain.

``enabled``
  Optional, boolean. Defaults to ``True``.
  Specifies if the configuration should be enabled by creating a symlink in
  :file:`/etc/nginx/sites-enabled/`.

``state``
  Optional, string. Defaults to ``present``.
  Whether the Nginx server should be ``present`` or ``absent``.

``when``
  Deprecated, optional, boolean. Use ``state: 'present'`` instead.

``delete``
  Deprecated, optional, boolean. Use ``state: 'absent'`` instead.

``by_role``
  Optional, string. Name of a Ansible role in the format ``ROLE_OWNER.ROLE_NAME`` which is
  responsible for the server configuration.

``type``
  Optional. Specify name of the template to use to generate nginx server
  configuration. Templates can extend other templates.

``webroot_create``
  Optional, boolean. Whether the role will create a server's root directory.
  Overrides ``nginx_webroot_create``.

``owner``
  Optional, string. Sets the owner of the server root.
  Overrides ``nginx_webroot_owner``.

  If specified, nginx will configure the server root to
  :file:`/srv/www/<owner>/sites/<name[0]>/public/`.

  If not specified, nginx will configure the server root to
  :file:`/srv/www/sites/<name[0]>/public/`.

  If it is set and no ``group`` is specified, the group is set to ``owner``.

``group``
  Optional, string. Explicitly sets the group of the server root.
  Overrides ``owner`` and ``nginx_webroot_group``.

``mode``
  Optional, string. The permissions of the server root directory.
  Overrides ``nginx_webroot_mode``.

.. _nginx__ref_servers_common_webserver_options:

Common webserver options
~~~~~~~~~~~~~~~~~~~~~~~~

``index``
  Optional, string or boolean (``False``).
  Space separated list of index filenames.
  The directive will be omitted if set to ``False``.

``root``
  Optional, string.
  Absolute path to server root to use for this server configuration.
  Defaults to :file:`/srv/www/sites/<name[0]>/public/`.
  See also ``owner`` parameter.
  The directive will be omitted if set to ``False``.

``public_dir_name``
  Optional, string.
  Folder name witch will be concatenated to :file:`/srv/www/sites/<name[0]>/`
  Defaults to :file:`public`.

``root_suffix``
  Optional, string.
  Used in scenario when the site root is in another subfoder.
  Example. The files are stored in ``/srv/www/sites/<name[0]>/public``,
  but in nginx the root needs to be ``/srv/www/sites/<name[0]>/public/current/pub``.
  Defaults to empty string.


``try_files``
  Optional, string. Defaults to ``nginx_default_try_files``.
  Checks for the existence of files in order, and returns the
  first file that is found for location /.
  Refer to the `Nginx try_files directive` for details.

``keepalive``
  Optional, integer. Defaults to ``nginx_default_keepalive_timeout``.
  Set custom KeepAlive timeout for this server, in seconds.

``deny_hidden``
  Optional, boolean. Defaults to ``True``.
  If ``True`` deny access to all hidden files.

``favicon``
  Optional, boolean. Defaults to ``True``.
  Ignore :file:`/favicon.ico` requests in server logs to reduce noise if
  ``True``.

``listen``
  Optional, list of strings/integers or boolean (``False``).
  Defaults to ``nginx_listen_port``.
  List of ports, IP addresses or sockets this server configuration should
  listen on for HTTP connections.

``listen_ssl``
  Optional, list of strings/integers or boolean (``False``).
  Defaults to ``nginx_listen_ssl_port``.
  List of ports, IP addresses or sockets this server configuration should
  listen on for HTTPS connections.

``include_files_begin``
  Optional, list of strings.
  List of files that will be included at the beginning of the server
  configuration using `include`.

``include_files_end``
  Optional, list of strings.
  List of files that will be included at the end of the server
  configuration using `include`.

``options``
  Optional, String or YAML text block with options for this server configuration.
  Semicolons at the end of each line are required.

Redirects
~~~~~~~~~

``redirect``
  Optional, string.
  Redirect incoming requests on the HTTP port to the given URL.
  FIXME: Rename to redirect_http

``redirect_ssl``
  Optional, string.
  Redirect incoming requests on the HTTPS port to the given URL.
  FIXME: Rename to redirect_https

``redirect_code``
  Optional, string. Specify HTTP code used in the redirect response, by default
  307 Temporary Redirect.
  FIXME: Rename to redirect_http_code

``redirect_code_ssl``
  Optional, string. Specify HTTP code used in the redirect response from HTTP to
  HTTPS, by default 301 Moved Permanently.
  FIXME: Rename to redirect_https_code

``redirect_from``
  Optional, list of strings or boolean.
  Create a separate `Nginx server block documentation`_ which will automatically redirect
  requests from specified list of server names (or all but the first name in
  the ``name`` list if ``redirect_from`` is set to ``True``) to the first
  server name specified in the ``name`` list.

``redirect_to``
  Optional, string. Create separate `Nginx server block documentation`_ which redirects all
  requests on servers specified in the ``name`` list to the server
  specified in ``redirect_to``. The specified server name will be used as
  the only name in subsequent HTTP and HTTPS configuration.

``redirect_to_ssl``
  Optional, boolean. Defaults to ``True``
  If ``True``, redirect connection from HTTP to the HTTPS version of the site.
  Set to ``False`` to allow to serve the website via HTTP and HTTPS and don't
  redirect HTTP to HTTPS.
  FIXME: Rename to redirect_to_https


HTTPS and TLS
~~~~~~~~~~~~~

``acme``
  Optional, boolean. Defaults to ``nginx_acme``.
  Enable or disable support for Automated Certificate Management Environment
  challenge queries for this server.

``ssl``
  Optional, boolean. Defaults to ``nginx_pki``.
  Enable or disable HTTPS for this server configuration.
  FIXME: Rename to https_enabled

``ssl_crt``
  Optional, string. Absolute path to a custom X.509 certificate to use. If not
  supplied, a certificate managed by :ref:`debops.pki` will be used.
  FIXME: Rename to tls_cert

``ssl_key``
  Optional, string. Absolute path to custom private key to use. If not
  supplied ``pki_key`` will be used instead.
  FIXME: Rename to tls_key

``ssl_ca``
  Optional, string. Specifies the absolute path to the client CA certificate
  used to authenticate clients. If not specified, ``pki_ca`` will be used
  instead.

``ssl_trusted``
  Optional, string. Specifies the absolute path to the intermediate+root CA server
  certificates which will be used for OCSP stapling verification. If not
  specified, the value of ``pki_trusted`` will be used instead.

``ssl_dhparam``
  Optional, string. Absolute path to custom DHE parameters to use. If not supplied,
  ``nginx_ssl_dhparam`` will be used instead.
  FIXME: Rename to tls_dhparam_file

``ssl_ciphers``
  Optional, strings. Defaults to ``nginx_default_ssl_ciphers``.
  Name of the list of preferred server ciphers defined in ``nginx_ssl_ciphers`` to use.

``ssl_curve``
  Optional, string. Defaults to ``nginx_default_ssl_curve``.
  ECC curve enabled for this server.

``ssl_verify_client``
  Optional, boolean. Requests the client certificate and verifies it if the
  certificate is present.

``ssl_client_certificate``
  Optional, string. Specifies a file with trusted CA certificates in the PEM
  format used to verify client certificates.

``ssl_crl``
  Optional. Specifies a file with revoked certificates (CRL) in PEM
  format used to verify client certificates.

``pki_realm``
  Optional, string. Overwrites the default PKI realm used by nginx for this
  server configuration. See the :ref:`debops.pki` role for more information, as well
  as the :file:`/etc/pki/realms` directory on remote hosts for a list of
  available realms.

``pki_crt``
  Optional, string. Path to custom X.509 certificate to use, relative to the
  currently enabled PKI realm.

``pki_key``
  Optional, string. Path to custom private key to use, relative to the
  currently enabled PKI realm.

``pki_ca``
  Optional, string. Path to custom client CA certificate to use for client
  authentication, relative the to currently enabled PKI realm.

``pki_trusted``
  Optional, string. Path to custom intermediate+root CA certificate to use for
  OCSP stapling verification, relative to currently enabled PKI realm.

``ocsp``
  Optional, boolean. Defaults to ``nginx_ocsp``.
  Enable or disable OCSP stapling for a given server.
  FIXME: Rename to ocsp_stapling_enabled

``ocsp_verify``
  Optional, boolean. Defaults to ``nginx_ocsp_verify``
  Enable or disable OCSP stapling verification for a given server. An
  intermediate+root CA certificate is required for this.
  FIXME: Rename to ocsp_stapling_verify

``hsts_enabled``
  Optional, boolean. Defaults to ``True``. If this is set to ``True`` and HTTPS
  is enabled for this item, the `HTTP Strict Transport Security`_ header is set
  in the server's responses.  If this is set to ``False``, the header will not
  be set in the server's responses.

``hsts_preload``
  Optional, boolean. Defaults to ``nginx_hsts_preload``.
  Add a "preload" parameter to the HSTS header which can be used with the
  https://hstspreload.appspot.com/ site to configure HSTS preloading for a
  given website.


User authentication
~~~~~~~~~~~~~~~~~~~

``auth_basic``
  Optional, boolean. Enable HTTP Basic Authentication for this server.

``auth_basic_realm``
  Optional. String which will be displayed to the user in the HTTP Basic Auth
  dialog box.
  Defaults to ``nginx_default_auth_basic_realm``.

``auth_basic_name``
  Optional, string. Required with ``auth_basic``. Specifies the name of the
  htpasswd file used for this server authentication. htpasswd files are
  stored in :file:`/etc/nginx/private/` directory.

  You can use ``auth_basic_filename`` and specify the full path to the
  htpasswd file to use; file needs to be readable by nginx system user.


Locations
~~~~~~~~~

``location``
  Optional. Dict of location sections to include in this server configuration,
  in YAML text block format (semicolons at end of each configuration line
  required). Each key defines a string used as "location" option, values are
  strings or text blocks to be included inside each location section.
  Examples:

  .. code-block:: yaml
    :linenos:

     location:
       '/': 'try_files $uri $uri/ /index.html =404;'

       '~ ^/doc$': |
         alias /usr/share/doc;
         autoindex on;

``location_allow``
  Optional. Dict which adds "allow" entries to each location section defined
  above from a list. Each location needs to have a corresponding entry in
  ``location`` dict. If ``item.location_deny`` is not defined, 'deny all;' is
  added at the end. Examples:

  .. code-block:: yaml
    :linenos:

     location_allow:
       '~ ^/doc$': [ '127.0.0.1', '::1' ]

``location_deny``
  Optional. Dict which adds "deny" entries to each location section
  defined above from a list. Each location needs to have corresponding
  entry in ``location`` dict. Examples:

  .. code-block:: yaml
    :linenos:

     location_deny:
       '/': [ '192.168.0.1/24' ]
       '~ ^/doc$': [ 'all' ]

``location_referers``
  Optional. Dict with lists of valid referers accepted for a given
  location, all other referers will be blocked by nginx. Each location
  needs to have corresponding entry in ``location`` dict. Examples:

  .. code-block:: yaml
    :linenos:

     location_referers:
       '/': [ '{{ ansible_fqdn }}', 'www.{{ ansible_fqdn }}', '*.{{ ansible_domain }}' ]

``location_list``
  Optional, list of dicts. This is an alternative syntax of ``location_*``
  entries; instead of using text blocks directly, it uses dict keys and values
  to configure each location, which allows for greater control and nesting.
  List of known keys and their descriptions:

  ``pattern``
    Location string pattern, for example: ``/`` or ``~ ^/doc$`` or ``gitlab``

  ``pattern_prefix``
    String prepended to the location pattern, for example: ``@`` which will
    create the named location ``@gitlab``

  ``enabled``
    Boolean value specifying if the location should be included in
    configuration, defaults to ``True``.

  ``referers``
    List of allowed valid referer strings.

    .. code-block:: yaml
      :linenos:

       referers: [ '{{ ansible_fqdn }}' ]

  ``allow`` and ``deny``
    Lists of hosts or CIDR ranges to allow or deny, lack of deny implies
    ``deny all;`` at the end of the allow list.

  ``options``
    String or YAML text block with options for this location block, semicolons
    at the end of each line are required.

  ``locations``
    Nested list of locations to create in this location section.


.. _nginx__ref_servers_http_security_headers:

HTTP security headers
~~~~~~~~~~~~~~~~~~~~~

``csp``
  Optional, string. Defaults to: ``default-src https: ;`` (force all assets to be loaded over HTTPS).
  Sets the first part of the ``Content-Security-Policy`` header.
  The string MUST end with a semicolon but MUST NOT begin with one.
  Make sure that you only use single quotes and no double quotes in the string.
  If no ``item.csp_report`` is given, it also determines the first part of the
  ``Content-Security-Policy-Report-Only`` header.
  Which headers are actually enabled is defined by ``item.csp_enabled``
  and ``item.csp_report_enabled``.
  Refer to the `Content Security Policy Reference`_.

``csp_report``
  Optional, string. This allows to set a different/potentially experimental
  ``Content-Security-Policy-Report-Only`` header than defined by ``item.csp``.

``csp_append``
  Optional, string. Defaults to: :envvar:`nginx__http_csp_append`.
  CSP directives to append to all policies (``item.csp`` and ``item.csp_report``).
  This can be used to overwrite the default :envvar:`nginx__http_csp_append` as needed.
  The string MUST end with a semicolon but MUST NOT begin with one.

``csp_enabled``
  Optional, boolean. Defaults to ``False``.
  If set to ``True`` and HTTPS is enabled for this item, the
  ``Content-Security-Policy`` header is set in server responses.

``csp_report_enabled``
  Optional, boolean. Defaults to ``False``.
  If this is set to ``True`` and HTTPS is enabled for this item, the
  ``Content-Security-Policy-Report-Only`` header is set in the server responses.

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

.. _nginx__ref_http_referrer_policy:

``http_referrer_policy``
  Optional, string. Value of the ``Referrer-Policy`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to :envvar:`nginx__http_referrer_policy`.
  Refer to `Referrer Policy`_ for more details. Note that this header is a
  draft as of 2016-10-11 but it is already supported by the majority of web
  browsers.

.. _nginx__ref_permitted_cross_domain_policies:

``permitted_cross_domain_policies``
  Optional, string. Value of the ``X-Permitted-Cross-Domain-Policies`` HTTP header field. Set to
  ``{{ omit }}`` to not send the header field. Defaults to
  :envvar:`nginx__http_permitted_cross_domain_policies`.

  Should cross domain policies be permitted?

.. _nginx__ref_frame_options:

``frame_options``
  Optional, string. Value of the ``X-Frame-Options`` HTTP header field. Set to ``{{ omit }}``
  to not send the header field. Defaults to ``SAMEORIGIN``.

Search engine optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Access control
~~~~~~~~~~~~~~

``access_policy``
  Optional, string. Specify a named "access policy" to use for this server. Refer to
  ``nginx_access_policy_allow_map`` and similar variables for more
  information.

``satisfy``
  Optional, string. Defaults to ``nginx_default_satisfy``.
  Set the server behaviour to either accept any of ``allow, auth``
  configuration restrictions, or require all of them to match.  By default, any
  restriction by itself will match.  Choices: ``any``, ``all``

``allow``
  Optional, string or list of strings.
  IP addresses or CIDR networks which can access the given server.
  Automatically adds ``deny: all`` at the end of the list.

``options``
  Optional, string. Add custom options to this server configuration using a
  YAML text block (semicolons at the end of each line are required).


Logging and monitoring
~~~~~~~~~~~~~~~~~~~~~~

``log_path``
  Optional, string. Absolute path where log files should be stored. If not
  specified, logs will be saved to :file:`/var/log/nginx/` directory. You
  should take care of log rotation if you specify a custom log path.
  The specified path needs to exist before nginx is reloaded/restarted.

``access_log``
  Optional, string. Defaults to ``<``name[0]>_access``.
  Name of the access log file.
  The suffix ``.log`` will be added automatically.

``access_log_enabled``
  Optional, boolean. Defaults to ``True``.
  If access logging should be enabled.

``error_log``
  Optional, string. Defaults to ``<``name[0]>_error``.
  Name of the error log file.
  The suffix ``.log`` will be added automatically.

``error_log_enabled``
  Optional, boolean. Defaults to ``True``.
  If error logging should be enabled.

``access_log_format``
  Optional. Name of the access log format.
  Custom log formats can be defined using ``nginx__log_format`` variable.

``status``
  Optional, list of strings.
  Enable nginx server status page and allow access from the given list of IP
  addresses or CIDR ranges.

``status_name``
  Optional, string. Defaults to ``nginx_status_name``.
  Set the name of the location which should be used for the nginx status page.


Error pages
~~~~~~~~~~~

``error_pages``
  Optional. Dict of error codes in string format as keys and
  corresponding error pages to display. Example:

  .. code-block:: yaml
    :linenos:

     error_pages:
       '403 404': '/400.html'
       '502':     '/500.html'

``error_pages_list``
  Optional. List of dictionaries, each one describing an error page. List
  of known keys and their descriptions:

  ``code``
    Required, String or list strings. Error codes to include in this
    configuration section.

  ``uri``
    Required. URI or location to redirect the request to.

  ``location`` and ``location_options``
    Optional. If specified, an additional location section will be added
    with contents of the ``location_options`` parameter. If only
    ``location_options`` is present, the ``uri`` parameter will be used as
    the location.

  Examples:

  .. code-block:: yaml
    :linenos:

     error_pages_list:
       - code: [ '403', '404', '=500' ]
         uri: '/error.html'
         location: '= /error.html'
         location_options: |
           internal;

``maintenance``
  Optional, boolean. Defaults to ``True``.
  Specifies if the maintenance HTML page configuration should be added to the
  server or not.

``maintenance_file``
  Optional. Path of the maintenance HTML page (by default
  :file:`maintenance.html`) located in the website's document root directory.
  If the file is present, all requests will be redirected to the maintenance
  page with error "503 Service Unavailable".

Welcome page
~~~~~~~~~~~~

``welcome``
  Optional, boolean. Defaults to ``False``.
  If ``True`` a welcome :file:`index.html` page is generated in website root
  directory using a template.

``welcome_force``
  Optional, boolean.
  Ensure that the templated file is up-to-date if ``True``.
  Set to ``False`` by default to ensure idempotent operation.

``welcome_template``
  Optional. Specify absolute path to a Jinja2 template which should be
  used to generate a welcome page.

``welcome_domain``
  Optional. Specify a DNS domain which should be used in the generated
  welcome page. By default, a domain is detected from ``name[0]``, or
  if it's not specified, ``ansible_domain`` variables.

``welcome_css``
  Optional. If specified and False, omit custom stylesheet in the
  generated :file:`index.html`' file.


User directories
~~~~~~~~~~~~~~~~

``userdir``
  Optional, boolean. Enable UserDir support.
  Web pages on :file:`https://host/~<user>/` will be read from
  :file:`/srv/www/<user>/userdir/public` directories.

``userdir_regexp``
  Optional, string. Specify location regexp pattern used by nginx to determine if
  a specified URL is an userdir URL.

``userdir_alias``
  Optional, string. Specify the absolute path to user directories used as an
  alias pattern which uses the parameters from location regexp to select
  the correct user and file to display.

``userdir_index``
  Optional, string. Specify space separated list of index files which will be
  used by nginx automatically to display a HTML page, if found in the current
  directory.

``userdir_options``
  Optional, string. Specify additional options added to the userdir location
  block.

.. _nginx__ref_servers_php:

Type: php
~~~~~~~~~

Available when ``item.type`` is set to ``php`` for a server.

``php_upstream``
  Required, string. Name of nginx upstream to use.

  If undefined, :file:`.php` files will be protected by =403.

``index``
  Optional, string.
  Space separated list of index filenames.
  Refer to :ref:`nginx__ref_servers_common_webserver_options` for details.

  If undefined, add :file:`index.php` at the end of list of index files.

``php_limit_except`` or False
  Optional, string or list of strings or boolean (``False``).
  Whitelist of allowed HTTP request methods.

  If absent or ``False``, limits are disabled.

  Refer to the `Nginx limit_except directive documentation`_ for details.

``php_include``
  Optional, string or boolean (``False``).
  File to include instead of :file:`fastcgi_params` or :file:`fastcgi.conf`,
  relative to :file:`/etc/nginx/`.

  If set to ``False``, nothing is included.

``php_try_files``
  Optional. A string or list with ``try_files`` option values which should be
  defined in the PHP location blocks. If not defined, the default is to use the
  ``$script_name`` and ``=404`` values.

``php_options``
  Optional, string. Additional options to append to php location.

``php_status``
  Optional, boolean. Enable php-fpm server status page.

``php_status_name``
  Optional, string. Defaults to ``php_status``.
  Set the name of the location which should be used for php fpm
  status page

``php_ping_name``
  Optional, string. Defaults to ``php_ping``.
  Set the name of the location which should be used for php fpm
  ping page

``php_status_allow``
  Optional, string or list of strings.
  Allow access the given IP addresses or CIDR ranges.

Type: php5
~~~~~~~~~~

Deprecated, use :ref:`nginx__ref_servers_php`.

Type: proxy
~~~~~~~~~~~

Available when ``item.type`` is set to ``proxy`` for a server.

``proxy_pass``
  Required, string. Set the upstream url for this proxy configuration. This can
  be omitted if either a ``location`` or a ``location_list`` is defined.

``proxy_location``
  Optional, string. Defaults to ``/``.
  Set the location for the proxy, which is used in case not other ``location`` or
  ``location_list`` are defined.

``proxy_headers``
  Optional, string. Add custom headers to this proxy configuration using a YAML
  text block (semicolon at the end of each line is required).

``proxy_options``
  Optional, string. Add custom options to this proxy configuration using a YAML
  text block (semicolon at the end of each line is required).

Type: rails
~~~~~~~~~~~

Available when ``item.type`` is set to ``rails`` for a server.

FIXME: Documentation missing.

.. _Nginx server_name option documentation: https://nginx.org/en/docs/http/server_names.html
.. _Nginx server block documentation: https://nginx.org/en/docs/http/ngx_http_core_module.html#server
.. _Nginx try_files directive documentation: https://nginx.org/en/docs/http/ngx_http_core_module.html#try_files
.. _Nginx limit_except directive documentation: https://nginx.org/en/docs/http/ngx_http_core_module.html#limit_except
