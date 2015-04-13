Changelog
=========

v0.1.4
------

*Unreleased*

- Add an option to set ``client_max_body_size`` globally for entire nginx
  server, by setting ``nginx_http_client_max_body_size`` variable in Ansible
  inventory. [drybjed]

- Add DebOps pre-tasks and post-tasks hooks. [drybjed]

- Allow to override ``nginx_passenger_root`` and ``nginx_passenger_ruby``
  variables using Ansible inventory variables. [drybjed]

- Make sure that lists of IP addresses used in the templates are unique, this
  is required to eliminate duplicate IPv6 addresses in case of VLAN use.
  [drybjed]

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

