Changelog
=========

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

