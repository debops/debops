Changelog
=========

**debops.nginx**

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.nginx master`_ - unreleased
-----------------------------------

.. _debops.nginx master: https://github.com/debops/ansible-nginx/compare/v0.1.7...master

Added
~~~~~

- Add new PHP upstream and PHP server templates. [drybjed]

Changed
~~~~~~~

- Use the new ``debops.php`` fact to detect PHP version. [drybjed]

- Update Changelog format, add more documentation. [drybjed]

- Move the configuration of other roles to new namespaced variables, so
  playbooks can begin the switch. Old-style variables still work. [drybjed]

- Reorganize support for different ``nginx`` flavors to use YAML dictionary
  maps for APT key ids and APT repositories. Full GPG key ids are used to
  download APT repository keys. [drybjed]

- Update tasks that manage ``nginx`` upstreams, maps and custom configuration.
  These lists now support the ``item.state`` parameter to control when
  configuration files should be present or absent. [drybjed]

Deprecated
~~~~~~~~~~

- Some of the default variables are deprecated in this version. Below you can
  find a list with their replacements. The old variable names will still be
  recognized for some time. [drybjed]

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

- The ``php5`` server and upstream templates are deprecated in favour of
  ``php`` server and upstream templates. [drybjed]

Removed
~~~~~~~

- Remove the ``item.locked`` parameter from ``nginx`` server configuration
  parameters. [drybjed]


`debops.nginx v0.1.7`_ - 2016-06-14
-----------------------------------

.. _debops.nginx v0.1.7: https://github.com/debops/ansible-nginx/compare/v0.1.6...v0.1.7

Added
~~~~~

- Added ``nginx__deploy_state`` to allow to specify the desired state this role
  should achieve. State ``absent`` is not fully implemented yet. [ypid]

- Expose Nginx version via Ansible facts as ``ansible_local.nginx.version`` so
  that it can be used outside of this role.
  Check :file:`templates/etc/nginx/sites-available/default.conf.j2`
  for an example usage. [ypid]

Changed
~~~~~~~

- Changed the default value of the ``X-XSS-Protection`` HTTP header field from
  ``1`` (enabled), to ``1; mode=block`` (enabled and block rendering) for
  increased security and made the global default configurable via
  :any:`nginx__http_xss_protection`. Note that the ``mode=block`` might create
  `a vulnerability in old versions of Internet Explorer
  <https://github.com/helmetjs/helmet#xss-filter-xssfilter>`.
  Additionally, changed the header field from ``X-Xss-Protection`` to the more
  common one ``X-XSS-Protection`` (``XSS`` in all upper case). [ypid]

- Make the ``X-Robots-Tag`` HTTP header field configurable via
  ``item.robots_tag`` and :any:`nginx__http_robots_tag`. [ypid]

- Make the ``X-Permitted-Cross-Domain-Policies`` HTTP header field configurable
  via ``item.permitted_cross_domain_policies`` and
  :any:`nginx__http_permitted_cross_domain_policies`. [ypid]

Fixed
~~~~~

- Fixed Ansible check mode. Check mode did fail when the role was trying to
  symlink a non-existing file. [ypid]


`debops.nginx v0.1.6`_ - 2016-03-07
-----------------------------------

.. _debops.nginx v0.1.6: https://github.com/debops/ansible-nginx/compare/v0.1.5...v0.1.6

Added
~~~~~

- Add support for defining error pages in a list, with better control over
  their configuration. [drybjed]

Changed
~~~~~~~

- Do not create welcome pages automatically if creation of webroot directories
  is disabled. [drybjed]

- Make sure that ``/var/lib/nginx/`` directory exists. [pedroluislopez]

- Ensure that list of site referers is unique. [drybjed]

- Use an absolute path in the ``nginx`` PKI hook for ``service`` command, since
  it's outside of the default ``$PATH`` defined by ``cron``. [drybjed]


`debops.nginx v0.1.5`_ - 2016-02-07
-----------------------------------

.. _debops.nginx v0.1.5: https://github.com/debops/ansible-nginx/compare/v0.1.4...v0.1.5

Added
~~~~~

- Create a proof-of-concept "solo" version of the role, that does not include
  additional Ansible role dependencies. [drybjed]

- Add default ``localhost`` nginx server. It has disabled HTTPS support and can
  be used by other applications to get the nginx status page locally. [drybjed]

- Add support for getting the client IP address from a custom header, when
  ``nginx`` is used behind a proxy server. [drybjed]

- Add a way to control if ``debops.nginx`` role automatically adds
  ``ipv6only=false`` to the configuration to support dual-stack IPv4/IPv6
  connections. This was the default, now it can be disabled so that users can
  control the listening ports themselves. [drybjed]

- Add support for ``HTTP/2`` deprecating ``SPDY`` in ``nginx`` 1.9.5.
  [MatthewMi11er]

- Add support for Automated Certificate Management Environment (ACME)
  challenges. [drybjed]

- Provide a clean and simple welcome page which is displayed by default if
  specified server does not exist. The welcome page will be generated only if
  ``index.html`` is not present in the webroot directory. [drybjed]

- Add a hook script in ``/etc/pki/hooks/`` directory. When certificates used by
  ``nginx`` are changed, it will reload the webserver to enable them. [drybjed]

Changed
~~~~~~~

- Switch from using Diffie-Hellman parameters generated by ``debops.pki`` role
  to DH parameters managed by ``debops.dhparam`` role. [drybjed]

- Most of the file paths used by ``nginx`` are now configurable using default
  variables. This allows to run ``nginx`` on an unprivileged account.

  ``nginx_root_www_path`` variable has been renamed to ``nginx_www``. [drybjed]

- Allow configuration of default ``listen`` and ``listen_ssl`` directives using
  default variables. [drybjed]

- Move configuration of ``debops.nginx`` role dependencies to default
  variables. It can be used to configure firewall and APT preferences using
  Ansible playbooks instead of hardcoding the dependencies in the role itself.

  Existing role dependencies are still used, and will be removed once all
  involved application playbooks which depend on ``debops.nginx`` are updated.
  [drybjed]

- Update ``localhost`` server to also accept connections on loopback IP
  addresses, so that check plugins like ``check_mk`` can work correctly. [ypid]

- Wrap the default HTTP redirect configuration in ``location / {}`` section.
  This allows addition of other location sections as necessary without breaking
  the page. [drybjed]

- Support ``item.options`` YAML text block in nginx upstreams. [drybjed]

- Move the ``root`` parameter to its own macro block and use it separately in
  HTTP and HTTPS server configuration section. This is needed for the HTTP
  configuration to serve files from a sane directory. [drybjed]

- Don't print ``root`` option in the ``nginx`` server configuration if it's set
  as ``False`` (shouldn't be used, but it is checked just in case). [drybjed]

- Make sure that ``root`` and ACME configuration is not added two times when
  HTTP listen configuration is disabled. [drybjed]

- Clean up default variables related to ``debops.pki`` role, add variables that
  configure client CA and trusted CA for OCSP stapling in ``default.conf``
  template. [drybjed]

- Update OCSP stapling support. Two new default variables are added to better
  control OCSP configuration.

  The ``debops.nginx`` role will now use the trusted certificate chain from
  ``debops.pki`` by default. The caveat is, if at least a Root CA certificate
  is not provided in the ``debops.pki`` realm, ``nginx`` configuration will be
  invalid and restarting the webserver will fail. Right now you can avoid this
  by setting ``nginx_ocsp_verify`` variable to ``False`` if needed, there's
  also per-vhost ``item.ocsp_verify`` rquivalent.

  The internal ``debops.pki`` certificates should work out of the box.
  [drybjed]

- Support autodetection of PKI realms.

  The ``debops.nginx`` role will check if any of the server names for a given
  vhost have corresponding PKI realms. If a corresponding realm is found, its
  certificates will be used for that server, unless overriden by
  ``item.pki_realm`` parameter. If a corresponding realm is not found, that
  vhost will use the default PKI realm. [drybjed]

- Support `HSTS preloading <https://hstspreload.appspot.com/>`_ in ``nginx``
  server configuration. [drybjed]

- Reorganize server, upstream and map default variables.

  The ``nginx_servers`` variable has been split into

  - ``nginx_default_servers`` (default welcome page of the server);
  - ``nginx_internal_servers`` (``localhost`` and ``acme`` servers);
  - ``nginx_dependent_servers`` (webservers managed by other roles);

  Similar split has been done with ``nginx_upstreams`` and ``nginx_maps``
  variables. The order of the variables is designed so that if you configure an
  ``nginx`` website in the ``nginx_servers`` list (the same as up until now),
  the first one on the list will be marked as default, easily overriding the
  welcome page defined in ``nginx_default_servers``.

  The ``nginx_server_default`` dictionary variable has been renamed to
  ``nginx_server_welcome`` and now defines the default welcome page. You might
  need to update the Ansible inventory.

  The ``nginx_upstream_php5`` dictionary variable has been renamed to
  ``nginx_upstream_php5_www_data`` to be more specific. It defines an upstream
  for the default ``www-data`` PHP5 pool used by various services packaged in
  Debian. You might need to update the Ansible inventory. [drybjed]

- The default "welcome page" ``nginx`` server will use the ``welcome`` server
  name, so that role users can use empty name (``[]``) parameter in Ansible
  inventory without the configuration being constantly overwritten in an
  idempotency loop. The welcome page automatically gets its own web root
  directory ``/srv/www/sites/welcome/public/``, and shouldn't conflict with the
  default root.

  This shouldn't affect the effect of ``default_server`` option. The
  ``welcome`` "hostname" most likely won't ever be present in the DNS and
  nothing should directly point to it. [drybjed]

- Create the specified ``nginx`` maps and upstreams even when ``nginx_maps``
  and ``nginx_upstreams`` lists are empty. [drybjed]

Removed
~~~~~~~

- Remove the "solo" version of the role, a different concept will be created in
  its place. [drybjed]

- Remove ``item.pki`` in favor of ``item.ssl`` in the nginx site configuration.
  [patrickheeney]

- Remove ``nginx_default_root`` variable. A default root directory is managed
  dynamically in the ``default.conf`` server template. [drybjed]

Fixed
~~~~~

- Fix https site detection when using debops.nginx as a dependency.
  [patrickheeney]

- Fix bare variables due to deprecation. [drybjed]


`debops.nginx v0.1.4`_ - 2015-09-24
-----------------------------------

.. _debops.nginx v0.1.4: https://github.com/debops/ansible-nginx/compare/v0.1.3...v0.1.4

Added
~~~~~

- Add an option to set ``client_max_body_size`` globally for entire nginx
  server, by setting ``nginx_http_client_max_body_size`` variable in Ansible
  inventory. [drybjed]

- Add DebOps pre-tasks and post-tasks hooks. [drybjed]

- Add an option to set custom index files in nginx configuration. [drybjed]

- Add ``item.redirect_to`` key which lets you redirect connection from all
  server names listed in ``item.name`` to a specific server name (inverse
  ``item.redirect_from``). [drybjed]

- Add support for ``nginx`` package from upstream (http://nginx.org/), thanks
  to Pedro Luis López Sánchez. [drybjed]

- Add ``proxy`` nginx server template. [drybjed]

- Add ``item.ssl_crt``, ``item.ssl_key``, and ``item.ssl_dhparam`` to override
  pki nginx configuration per site. [patrickheeney]

- Added ``enabled`` to entries in ``item.location_list``. [scibi]

Changed
~~~~~~~

- Allow to override ``nginx_passenger_root`` and ``nginx_passenger_ruby``
  variables using Ansible inventory variables. [drybjed]

- Make sure that lists of IP addresses used in the templates are unique, this
  is required to eliminate duplicate IPv6 addresses in case of VLAN use.
  [drybjed]

- Move most of the http options from ``/etc/nginx/nginx.conf`` template to
  ``nginx_http_options`` YAML text block for easy modification if necessary.
  [drybjed]

- By default access to hidden files is blocked in ``nginx`` servers,
  ``item.deny_hidden`` key allows you to disable that. [drybjed]

- Filter out ``link-local`` IPv6 addresses from list of addresses that can
  access the ``/nginx_status`` page. [drybjed]

- Change how list of nameservers is gathered from ``/etc/resolv.conf`` to fix
  an issue with ``sed`` in shell command. [drybjed]

- Use ``fastcgi_params`` instead of ``fastcgi.conf`` as the FastCGI parameters
  file when ``nginx.org`` flavor is installed, because it is not provided by
  the non-Debian packages. On ``passenger`` and ``nginx.org`` flavors, missing
  ``SCRIPT_FILENAME`` parameter will be added directly in nginx server
  configuration. [drybjed]

- Update userdir support to be more configurable. [drybjed]

- Use all available nameservers as OCSP resolvers instead of just the first
  one. User can also override the list of OCSP resolvers if needed. [drybjed]

- Rearrange parts of the configuration templates and add more Jinja blocks to
  be able to remove ``index`` and ``root`` directives programatically.
  [drybjed]

Fixed
~~~~~

- Fix an issue where ``nginx`` used SSL configuration when support for it was
  disabled in ``debops.pki`` (or it was not present). [drybjed]


`debops.nginx v0.1.3`_ - 2015-03-27
-----------------------------------

.. _debops.nginx v0.1.3: https://github.com/debops/ansible-nginx/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add support for custom configuration templates using text blocks. [drybjed]

Changed
~~~~~~~

- Be more explicit while getting the list of nameservers from
  ``/etc/resolv.conf`` [drybjed]


`debops.nginx v0.1.2`_ - 2015-03-13
-----------------------------------

.. _debops.nginx v0.1.2: https://github.com/debops/ansible-nginx/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add a way to redirect HTTP site to HTTPS conditionally, with configuration
  being set in a separate file. [drybjed]

Changed
~~~~~~~

- Switch to older version of ``/etc/nginx/fastcgi_params`` when Phusion
  Passenger is enabled, because Passenger packages do not provide
  ``/etc/nginx/fastcgi.conf`` configuration file at the moment. [drybjed]


`debops.nginx v0.1.1`_ - 2015-03-12
-----------------------------------

.. _debops.nginx v0.1.1: https://github.com/debops/ansible-nginx/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add support for `Phusion Passenger`_ nginx flavor, using external APT
  packages. [rchady, drybjed]

Changed
~~~~~~~

- Automatically enable or disable SSL support in ``nginx`` depending on the
  presence or absence of ``debops.pki`` local Ansible facts. [drybjed]

.. _Phusion Passenger: https://www.phusionpassenger.com/


debops.nginx v0.1.0 - 2015-02-11
--------------------------------

Added
~~~~~

- First release, add CHANGES.rst [drybjed]
