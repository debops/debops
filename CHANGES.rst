Changelog
=========

v0.1.4
------

*Released: 2015-09-24*

- Add an option to set ``client_max_body_size`` globally for entire nginx
  server, by setting ``nginx_http_client_max_body_size`` variable in Ansible
  inventory. [drybjed]

- Add DebOps pre-tasks and post-tasks hooks. [drybjed]

- Allow to override ``nginx_passenger_root`` and ``nginx_passenger_ruby``
  variables using Ansible inventory variables. [drybjed]

- Make sure that lists of IP addresses used in the templates are unique, this
  is required to eliminate duplicate IPv6 addresses in case of VLAN use.
  [drybjed]

- Add an option to set custom index files in nginx configuration. [drybjed]

- Add ``item.redirect_to`` key which lets you redirect connection from all
  server names listed in ``item.name`` to a specific server name (inverse
  ``item.redirect_from``). [drybjed]

- Move most of the http options from ``/etc/nginx/nginx.conf`` template to
  ``nginx_http_options`` YAML text block for easy modification if necessary.
  [drybjed]

- Add support for ``nginx`` package from upstream (http://nginx.org/), thanks
  to Pedro Luis López Sánchez. [drybjed]

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

- Fix an issue where ``nginx`` used SSL configuration when support for it was
  disabled in ``debops.pki`` (or it was not present). [drybjed]

- Rearrange parts of the configuration templates and add more Jinja blocks to
  be able to remove ``index`` and ``root`` directives programatically.
  [drybjed]

- Add ``proxy`` nginx server template. [drybjed]

- Add ``item.ssl_crt``, ``item.ssl_key``, and ``item.ssl_dhparam`` to override
  pki nginx configuration per site. [patrickheeney]

- Added ``enabled`` to entries in ``item.location_list``. [scibi]

v0.1.3
------

*Released: 2015-03-27*

- Be more explicit while getting the list of nameservers from
  ``/etc/resolv.conf`` [drybjed]

- Add support for custom configuration templates using text blocks. [drybjed]

v0.1.2
------

*Released: 2015-03-13*

- Add a way to redirect HTTP site to HTTPS conditionally, with configuration
  being set in a separate file. [drybjed]

- Switch to older version of ``/etc/nginx/fastcgi_params`` when Phusion
  Passenger is enabled, because Passenger packages do not provide
  ``/etc/nginx/fastcgi.conf`` configuration file at the moment. [drybjed]

v0.1.1
------

*Released: 2015-03-12*

- Add support for `Phusion Passenger`_ nginx flavor, using external APT
  packages. [rchady, drybjed]

- Automatically enable or disable SSL support in ``nginx`` depending on the
  presence or absence of ``debops.pki`` local Ansible facts. [drybjed]

.. _Phusion Passenger: https://www.phusionpassenger.com/

v0.1.0
------

*Released: 2015-02-11*

- First release, add CHANGES.rst [drybjed]

