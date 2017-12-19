Changelog
=========

.. include:: includes/all.rst

**debops.nginx**

This project adheres to `Semantic Versioning <http://semver.org/>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.nginx master`_ - unreleased
-----------------------------------

.. _debops.nginx master: https://github.com/debops/ansible-nginx/compare/v0.2.1...master

Added

- Add :envvar:`nginx__log_format` and :envvar:`nginx__dependent_log_format` variables
  which can be used to add custom :command:`nginx` log format. [le9i0nx_]

`debops.nginx v0.2.1`_ - 2017-10-18
-----------------------------------

.. _debops.nginx v0.2.1: https://github.com/debops/ansible-nginx/compare/v0.2.0...v0.2.1

Added
~~~~~

- Support to disable :envvar:`nginx_acme_domain`. [ypid_]

- Support simple maintenance mode using a static HTML page in the document root
  directory. [drybjed_]

- Add :envvar:`nginx_extra_options` variable which can be used to add
  :command:`nginx` configuration outside of the ``http`` block in the
  :file:`/etc/nginx/nginx.conf` configuration file. [drybjed_]

- Add a default :command:`nginx` map used to upgrade HTTP connections to
  WebSockets, usually used in reverse proxy configuration. [drybjed_]

Changed
~~~~~~~

- ``item.frame_option`` and ``item.content_type_options`` can now be set to the
  special value ``{{ omit }}`` to omit their corresponding HTTP headers in
  nginx servers. [ypid_]

Fixed
~~~~~

- Fixed the usage of :envvar:`nginx_default_ssl_verify_client` when
  :envvar:`nginx_ocsp` is set to ``False``.
  :envvar:`nginx_default_ssl_verify_client` does not depend on :envvar:`nginx_ocsp`. [ypid_]

- CSP for welcome server did not end with a semicolon resulting in an invalid CSP with
  :envvar:`nginx__http_csp_append` set. [ypid_]


`debops.nginx v0.2.0`_ - 2017-04-15
-----------------------------------

.. _debops.nginx v0.2.0: https://github.com/debops/ansible-nginx/compare/v0.1.9...v0.2.0

Added
~~~~~

- ``item.welcome_force`` which when set to ``True`` will ensure that the
  welcome page is up-to-date. Note that setting this to ``True`` will not allow
  idempotent operation. [ypid_]

- Add/Set the default `Referrer Policy`_ to ``same-origin`` and made it
  configurable via :ref:`http_referrer_policy <nginx__ref_http_referrer_policy>`.

  Also set the `Referrer Policy`_ in the welcome page as HTML meta option as
  some website checkers like https://webbkoll.dataskydd.net/en seem to not get
  the HTTP header option yet.

  Note that ``no-referrer`` was originally used in an unreleased version of the
  role but this seemed to cause issues with certain applications so it was
  changed to ``same-origin`` by default. ``no-referrer`` can still be used when
  you know it does not break anything. [ypid_, drybjed_, scibi_]

Changed
~~~~~~~

- Standardize names of sites folders (`site-default` renamed to `sites-default`). [thiagotalma_]

- During configuration, role will check the list of names of a given :program:`nginx`
  server against the list of configured PKI realms to see if any name is
  a subdomain of domain with an existing PKI realm. If such PKI realm is found,
  it will be used for this server instead of the default one. [drybjed_]

- The URL scheme for the welcome page now defaults to ``HTTPS``. It can be
  configured as needed using the ``item.welcome_url_scheme`` option. [ypid_]

- Update to the latest recommenced set of ciphers suites from
  https://bettercrypto.org/. [ypid_]

- Rework the welcome page. Update to HTML5, make status configurable, define
  `Content Security Policy`, fix warnings and one templating error for
  ``nginx_tpl_welcome_title``. [ypid_]

- Increase Ansible min version to ``2.1.5``. Everything below is deprecated
  anyway and has vulnerabilities so you don’t want to use that anymore. [ypid_]

- Change :envvar:`nginx_hsts_preload` from ``True`` to ``False`` by default.
  Setting this value to ``True`` alone does not achieve anything and can
  actually cause problems if you are not prepared.
  Thus it is disabled by default.
  If you are ready for the future of HTTPS and TLS only, you are encouraged to
  enable it! [ypid_]

- Redesign Content Security Policy support of the role.
  ``item.csp_policy`` has been renamed to ``item.csp`` and the original
  ``item.csp`` is now called ``item.csp_enabled``.
  It is now also possible to set a global ``report-uri`` for all CSPs.
  The role will assert that it is being used with the redesigned interface and
  will fail if it is not. You will need to update your role/playbook/inventory.
  Refer to :ref:`nginx__ref_servers_http_security_headers`. [ypid_]

Deprecated
~~~~~~~~~~

- Deprecated the ``item.when`` and ``item.delete`` options. Use ``item.state`` instead. [ypid_]

- Deprecated the ``php5`` server type in favor to :ref:`nginx__ref_servers_php`. [ypid_]

Removed
~~~~~~~

- Remove the ``debops_nginx`` Ansible inventory group. Make sure you hosts
  are in ``debops_service_nginx``. [ypid_]

- Remove the Ansible role dependencies. Make sure that role dependencies get
  executed in the playbook and get the depend variables of the role passed.
  ``nginx_dependencies`` has no effect anymore and can be removed from your
  inventory if you used it. [ypid_]

Fixed
~~~~~

- Usage of an empty list for the ``name`` option of :envvar:`nginx__servers` items as documented. [ypid_]

- Fixed :ref:`xss_protection <nginx__ref_http_xss_protection>` which
  unintentionally determined if the
  :ref:`robots_tag <nginx__ref_http_robots_tag>` header was set for a given
  Nginx server. [ypid_]

- Make sure that the default HTTP server is selected even when ``item.listen``
  parameter is not specified in any of the server configuration entries.
  [drybjed_]

- Make sure that the configuration is generated correctly when HSTS preload is
  disabled. [drybjed_]


`debops.nginx v0.1.9`_ - 2016-07-19
-----------------------------------

.. _debops.nginx v0.1.9: https://github.com/debops/ansible-nginx/compare/v0.1.8...v0.1.9

Changed
~~~~~~~

- Make sure that lists of IP addresses are always defined. [thiagotalma_]

Security
~~~~~~~~

- Mitigate `HTTPOXY <https://httpoxy.org/>`_ attack on PHP applications
  server-side. [drybjed_]


`debops.nginx v0.1.8`_ - 2016-07-13
-----------------------------------

.. _debops.nginx v0.1.8: https://github.com/debops/ansible-nginx/compare/v0.1.7...v0.1.8

Added
~~~~~

- Add new PHP upstream and PHP server templates. [drybjed_]

- Support custom log directory path for nginx servers, specified by
  ``item.log_path`` parameter. [drybjed_]

Changed
~~~~~~~

- Use the new debops.php_ fact to detect PHP version. [drybjed_]

- Update Changelog format, add more documentation. [drybjed_]

- Move the configuration of other roles to new namespaced variables, so
  playbooks can begin the switch. Old-style variables still work. [drybjed_]

- Reorganize support for different :program:`nginx` flavors to use YAML dictionary
  maps for APT key ids and APT repositories. Full GPG key ids are used to
  download APT repository keys. [drybjed_]

- Update tasks that manage :program:`nginx` servers, upstreams, maps and custom
  configuration. These lists now support the ``item.state`` parameter to
  control when configuration files should be present or absent. [drybjed_]

- The ``item.enabled`` parameter in servers, maps, upstreams is now optional
  and if not specified, results in ``True``. [drybjed_]

- Passwords used by ``htpasswd`` will now be hashes using ``sha512_crypt``
  scheme. The default HTTP Basic Auth configuration variable is renamed from
  ``nginx_htpasswd_default`` to :envvar:`nginx__http_auth_htpasswd`.  New
  :envvar:`nginx__dependent_htpasswd` list can be used by other roles to create
  ``htpasswd`` files as needed. [drybjed_]

- You can now specify single server name in ``item.name`` parameter as a string
  instead of using a list notation. Lists are still supported. [drybjed_]

- Direct output of ``service nginx reload`` in the :program:`nginx` PKI hook script to
  :file:`/dev/null`. This should stop annoying emails from :program:`cron` each time
  :program:`nginx` service is reloaded after certificate changes. [drybjed_]

- Move variables from :file:`vars/main.yml` to :file:`defaults/main.yml` to allow
  modification. [drybjed_]

Deprecated
~~~~~~~~~~

- Some of the default variables are deprecated in this version. Below you can
  find a list with their replacements. The old variable names will still be
  recognized for some time. [drybjed_]

  +------------------------------------------+--------------------------------------------+
  | Deprecated variable                      | New variable                               |
  +==========================================+============================================+
  | ``nginx_apt_preferences_dependent_list`` | ``nginx__apt_preferences__dependent_list`` |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_ferm_dependent_rules``           | ``nginx__ferm__dependent_rules``           |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_maps``                           | ``nginx__maps``                            |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_default_maps``                   | ``nginx__default_maps``                    |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_dependent_maps``                 | ``nginx__dependent_maps``                  |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_upstreams``                      | ``nginx__upstreams``                       |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_default_upstreams``              | ``nginx__default_upstreams``               |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_dependent_upstreams``            | ``nginx__dependent_upstreams``             |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_custom_config``                  | ``nginx__custom_config``                   |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_servers``                        | ``nginx__servers``                         |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_default_servers``                | ``nginx__default_servers``                 |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_internal_servers``               | ``nginx__internal_servers``                |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_dependent_servers``              | ``nginx__dependent_servers``               |
  +------------------------------------------+--------------------------------------------+
  | ``nginx_htpasswd``                       | ``nginx__htpasswd``                        |
  +------------------------------------------+--------------------------------------------+

- The ``php5`` server and upstream templates are deprecated in favor of
  ``php`` server and upstream templates. [drybjed_]

Removed
~~~~~~~

- Remove the ``item.locked`` parameter from :program:`nginx` server configuration
  parameters. [drybjed_]


`debops.nginx v0.1.7`_ - 2016-06-14
-----------------------------------

.. _debops.nginx v0.1.7: https://github.com/debops/ansible-nginx/compare/v0.1.6...v0.1.7

Added
~~~~~

- Added :envvar:`nginx__deploy_state` to allow to specify the desired state this role
  should achieve. State ``absent`` is not fully implemented yet. [ypid_]

- Expose Nginx version via Ansible facts as ``ansible_local.nginx.version`` so
  that it can be used outside of this role.
  Check :file:`templates/etc/nginx/sites-available/default.conf.j2`
  for an example usage. [ypid_]

Changed
~~~~~~~

- Changed the default value of the ``X-XSS-Protection`` HTTP header field from
  ``1`` (enabled), to ``1; mode=block`` (enabled and block rendering) for
  increased security and made the global default configurable via
  :envvar:`nginx__http_xss_protection`. Note that the ``mode=block`` might create
  `a vulnerability in old versions of Internet Explorer
  <https://github.com/helmetjs/helmet#xss-filter-xssfilter>`.
  Additionally, changed the header field from ``X-Xss-Protection`` to the more
  common one ``X-XSS-Protection`` (``XSS`` in all upper case). [ypid_]

- Make the ``X-Robots-Tag`` HTTP header field configurable via
  ``item.robots_tag`` and :envvar:`nginx__http_robots_tag`. [ypid_]

- Make the ``X-Permitted-Cross-Domain-Policies`` HTTP header field configurable
  via ``item.permitted_cross_domain_policies`` and
  :envvar:`nginx__http_permitted_cross_domain_policies`. [ypid_]

Fixed
~~~~~

- Fixed Ansible check mode. Check mode did fail when the role was trying to
  symlink a non-existing file. [ypid_]


`debops.nginx v0.1.6`_ - 2016-03-07
-----------------------------------

.. _debops.nginx v0.1.6: https://github.com/debops/ansible-nginx/compare/v0.1.5...v0.1.6

Added
~~~~~

- Add support for defining error pages in a list, with better control over
  their configuration. [drybjed_]

Changed
~~~~~~~

- Do not create welcome pages automatically if creation of webroot directories
  is disabled. [drybjed_]

- Make sure that :file:`/var/lib/nginx/` directory exists. [pedroluislopez_]

- Ensure that list of site referers is unique. [drybjed_]

- Use an absolute path in the :program:`nginx` PKI hook for ``service`` command, since
  it's outside of the default ``$PATH`` defined by :program:`cron`. [drybjed_]


`debops.nginx v0.1.5`_ - 2016-02-07
-----------------------------------

.. _debops.nginx v0.1.5: https://github.com/debops/ansible-nginx/compare/v0.1.4...v0.1.5

Added
~~~~~

- Create a proof-of-concept "solo" version of the role, that does not include
  additional Ansible role dependencies. [drybjed_]

- Add default ``localhost`` nginx server. It has disabled HTTPS support and can
  be used by other applications to get the nginx status page locally. [drybjed_]

- Add support for getting the client IP address from a custom header, when
  :program:`nginx` is used behind a proxy server. [drybjed_]

- Add a way to control if ``debops.nginx`` role automatically adds
  ``ipv6only=false`` to the configuration to support dual-stack IPv4/IPv6
  connections. This was the default, now it can be disabled so that users can
  control the listening ports themselves. [drybjed_]

- Add support for ``HTTP/2`` deprecating ``SPDY`` in :program:`nginx` 1.9.5.
  [MatthewMi11er]

- Add support for Automated Certificate Management Environment (ACME)
  challenges. [drybjed_]

- Provide a clean and simple welcome page which is displayed by default if
  specified server does not exist. The welcome page will be generated only if
  ``index.html`` is not present in the webroot directory. [drybjed_]

- Add a hook script in :file:`/etc/pki/hooks/` directory. When certificates used by
  :program:`nginx` are changed, it will reload the webserver to enable them. [drybjed_]

Changed
~~~~~~~

- Switch from using Diffie-Hellman parameters generated by debops.pki_ role
  to DH parameters managed by debops.dhparam_ role. [drybjed_]

- Most of the file paths used by :program:`nginx` are now configurable using default
  variables. This allows to run :program:`nginx` on an unprivileged account.

  ``nginx_root_www_path`` variable has been renamed to ``nginx_www``. [drybjed_]

- Allow configuration of default ``listen`` and ``listen_ssl`` directives using
  default variables. [drybjed_]

- Move configuration of ``debops.nginx`` role dependencies to default
  variables. It can be used to configure firewall and APT preferences using
  Ansible playbooks instead of hardcoding the dependencies in the role itself.

  Existing role dependencies are still used, and will be removed once all
  involved application playbooks which depend on ``debops.nginx`` are updated.
  [drybjed_]

- Update ``localhost`` server to also accept connections on loopback IP
  addresses, so that check plugins like :command:`check_mk` can work correctly. [ypid_]

- Wrap the default HTTP redirect configuration in ``location / {}`` section.
  This allows addition of other location sections as necessary without breaking
  the page. [drybjed_]

- Support ``item.options`` YAML text block in nginx upstreams. [drybjed_]

- Move the ``root`` parameter to its own macro block and use it separately in
  HTTP and HTTPS server configuration section. This is needed for the HTTP
  configuration to serve files from a sane directory. [drybjed_]

- Don't print ``root`` option in the :program:`nginx` server configuration if it's set
  as ``False`` (shouldn't be used, but it is checked just in case). [drybjed_]

- Make sure that ``root`` and ACME configuration is not added two times when
  HTTP listen configuration is disabled. [drybjed_]

- Clean up default variables related to debops.pki_ role, add variables that
  configure client CA and trusted CA for OCSP stapling in :file:`default.conf`
  template. [drybjed_]

- Update OCSP stapling support. Two new default variables are added to better
  control OCSP configuration.

  The ``debops.nginx`` role will now use the trusted certificate chain from
  debops.pki_ by default. The caveat is, if at least a Root CA certificate
  is not provided in the debops.pki_ realm, :program:`nginx` configuration will be
  invalid and restarting the webserver will fail. Right now you can avoid this
  by setting ``nginx_ocsp_verify`` variable to ``False`` if needed, there's
  also per-vhost ``item.ocsp_verify`` equivalent.

  The internal debops.pki_ certificates should work out of the box.
  [drybjed_]

- Support autodetection of PKI realms.

  The ``debops.nginx`` role will check if any of the server names for a given
  vhost have corresponding PKI realms. If a corresponding realm is found, its
  certificates will be used for that server, unless overridden by
  ``item.pki_realm`` parameter. If a corresponding realm is not found, that
  vhost will use the default PKI realm. [drybjed_]

- Support `HSTS preloading <https://hstspreload.appspot.com/>`_ in :program:`nginx`
  server configuration. [drybjed_]

- Reorganize server, upstream and map default variables.

  The ``nginx_servers`` variable has been split into

  - ``nginx_default_servers`` (default welcome page of the server);
  - ``nginx_internal_servers`` (``localhost`` and ``acme`` servers);
  - ``nginx_dependent_servers`` (webservers managed by other roles);

  Similar split has been done with ``nginx_upstreams`` and ``nginx_maps``
  variables. The order of the variables is designed so that if you configure an
  :program:`nginx` website in the ``nginx_servers`` list (the same as up until now),
  the first one on the list will be marked as default, easily overriding the
  welcome page defined in ``nginx_default_servers``.

  The ``nginx_server_default`` dictionary variable has been renamed to
  ``nginx_server_welcome`` and now defines the default welcome page. You might
  need to update the Ansible inventory.

  The ``nginx_upstream_php5`` dictionary variable has been renamed to
  ``nginx_upstream_php5_www_data`` to be more specific. It defines an upstream
  for the default ``www-data`` PHP5 pool used by various services packaged in
  Debian. You might need to update the Ansible inventory. [drybjed_]

- The default "welcome page" :program:`nginx` server will use the ``welcome`` server
  name, so that role users can use empty name (``[]``) parameter in Ansible
  inventory without the configuration being constantly overwritten in an
  idempotency loop. The welcome page automatically gets its own web root
  directory :file:`/srv/www/sites/welcome/public/`, and shouldn't conflict with the
  default root.

  This shouldn't affect the effect of ``default_server`` option. The
  ``welcome`` "hostname" most likely won't ever be present in the DNS and
  nothing should directly point to it. [drybjed_]

- Create the specified :program:`nginx` maps and upstreams even when ``nginx_maps``
  and ``nginx_upstreams`` lists are empty. [drybjed_]

Removed
~~~~~~~

- Remove the "solo" version of the role, a different concept will be created in
  its place. [drybjed_]

- Remove ``item.pki`` in favor of ``item.ssl`` in the nginx site configuration.
  [patrickheeney_]

- Remove ``nginx_default_root`` variable. A default root directory is managed
  dynamically in the :file:`default.conf` server template. [drybjed_]

Fixed
~~~~~

- Fix https site detection when using debops.nginx as a dependency.
  [patrickheeney_]

- Fix bare variables due to deprecation. [drybjed_]


`debops.nginx v0.1.4`_ - 2015-09-24
-----------------------------------

.. _debops.nginx v0.1.4: https://github.com/debops/ansible-nginx/compare/v0.1.3...v0.1.4

Added
~~~~~

- Add an option to set ``client_max_body_size`` globally for entire nginx
  server, by setting ``nginx_http_client_max_body_size`` variable in Ansible
  inventory. [drybjed_]

- Add DebOps pre-tasks and post-tasks hooks. [drybjed_]

- Add an option to set custom index files in nginx configuration. [drybjed_]

- Add ``item.redirect_to`` key which lets you redirect connection from all
  server names listed in ``item.name`` to a specific server name (inverse
  ``item.redirect_from``). [drybjed_]

- Add support for :program:`nginx` package from upstream (https://nginx.org/), thanks
  to Pedro Luis López Sánchez. [drybjed_]

- Add ``proxy`` nginx server template. [drybjed_]

- Add ``item.ssl_crt``, ``item.ssl_key``, and ``item.ssl_dhparam`` to override
  pki nginx configuration per site. [patrickheeney_]

- Added ``enabled`` to entries in ``item.location_list``. [scibi_]

Changed
~~~~~~~

- Allow to override ``nginx_passenger_root`` and ``nginx_passenger_ruby``
  variables using Ansible inventory variables. [drybjed_]

- Make sure that lists of IP addresses used in the templates are unique, this
  is required to eliminate duplicate IPv6 addresses in case of VLAN use.
  [drybjed_]

- Move most of the http options from :file:`/etc/nginx/nginx.conf` template to
  ``nginx_http_options`` YAML text block for easy modification if necessary.
  [drybjed_]

- By default access to hidden files is blocked in :program:`nginx` servers,
  ``item.deny_hidden`` key allows you to disable that. [drybjed_]

- Filter out ``link-local`` IPv6 addresses from list of addresses that can
  access the :file:`/nginx_status` page. [drybjed_]

- Change how list of nameservers is gathered from :file:`/etc/resolv.conf` to fix
  an issue with ``sed`` in shell command. [drybjed_]

- Use ``fastcgi_params`` instead of :file:`fastcgi.conf` as the FastCGI parameters
  file when ``nginx.org`` flavor is installed, because it is not provided by
  the non-Debian packages. On ``passenger`` and ``nginx.org`` flavors, missing
  ``SCRIPT_FILENAME`` parameter will be added directly in nginx server
  configuration. [drybjed_]

- Update ``userdir`` support to be more configurable. [drybjed_]

- Use all available nameservers as OCSP resolvers instead of just the first
  one. User can also override the list of OCSP resolvers if needed. [drybjed_]

- Rearrange parts of the configuration templates and add more Jinja blocks to
  be able to remove ``index`` and ``root`` directives programmatically.
  [drybjed_]

Fixed
~~~~~

- Fix an issue where :program:`nginx` used SSL configuration when support for it was
  disabled in debops.pki_ (or it was not present). [drybjed_]


`debops.nginx v0.1.3`_ - 2015-03-27
-----------------------------------

.. _debops.nginx v0.1.3: https://github.com/debops/ansible-nginx/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add support for custom configuration templates using text blocks. [drybjed_]

Changed
~~~~~~~

- Be more explicit while getting the list of nameservers from
  :file:`/etc/resolv.conf` [drybjed_]


`debops.nginx v0.1.2`_ - 2015-03-13
-----------------------------------

.. _debops.nginx v0.1.2: https://github.com/debops/ansible-nginx/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add a way to redirect HTTP site to HTTPS conditionally, with configuration
  being set in a separate file. [drybjed_]

Changed
~~~~~~~

- Switch to older version of :file:`/etc/nginx/fastcgi_params` when Phusion
  Passenger is enabled, because Passenger packages do not provide
  :file:`/etc/nginx/fastcgi.conf` configuration file at the moment. [drybjed_]


`debops.nginx v0.1.1`_ - 2015-03-12
-----------------------------------

.. _debops.nginx v0.1.1: https://github.com/debops/ansible-nginx/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add support for `Phusion Passenger`_ nginx flavor, using external APT
  packages. [rchady, drybjed_]

Changed
~~~~~~~

- Automatically enable or disable SSL support in :program:`nginx` depending on the
  presence or absence of debops.pki_ local Ansible facts. [drybjed_]

.. _Phusion Passenger: https://www.phusionpassenger.com/


debops.nginx v0.1.0 - 2015-02-11
--------------------------------

Added
~~~~~

- First release, add CHANGES.rst [drybjed_]
