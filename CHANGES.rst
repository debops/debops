Changelog
=========

.. include:: includes/all.rst

**debops.apache**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops.apache v0.1.0 - unreleased
----------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Add/Set the default `Referrer Policy`_ to ``no-referrer`` and made it
  configurable via :ref:`item.http_referrer_policy <apache__ref_vhost_http_referrer_policy>`.
  [ypid_]

- Add the :envvar:`apache__mpm_max_connections_per_child` variable to allow to
  configure the number of requests a child process should handle before
  terminating. [ypid_]

- Add support to enable and configure `Apache mod_status`_. You can set
  :envvar:`apache__status_enabled` to ``True`` to enable it and make the status
  page accessible from localhost. [ypid_]

- Add support for generic Apache template generation using the `Apache IfVersion directive`_.
  This feature can be configured by :envvar:`apache__config_use_if_version` and
  :envvar:`apache__config_min_version`. [ypid_]

Changed
~~~~~~~

- Change default virtual host server name from ``000-default`` to ``default.{{
  apache__domain }}`` to increase the changes that a valid certificate is
  available for this virtual host (either wildcard or SAN) in order to avoid
  the warning of Apache that the certificate is not valid for the server name. [ypid_]

- Change :envvar:`apache__hsts_preload` from ``True`` to ``False`` by default.
  Setting this value to ``True`` alone does not achieve anything and can
  actually cause problems if you are not prepared.
  Thus it is disabled by default.
  If you are ready for the future of HTTPS and TLS only, you are encouraged to
  enable it! [ypid_]

Fixed
~~~~~

- Fixed usage of :envvar:`apache__dependent_packages` for ``debops.apache``.
  Previously the variable was only considered when handed to the ``debops.apache/env`` role.
  Note that all dependency variables should be passed to the main
  ``debops.apache`` role to avoid confusion. :envvar:`apache__dependent_packages` now
  only works when passed to the main role.

- Ensure that the shared object cache provider module is loaded when required
  for :envvar:`apache__ocsp_stapling_cache`. Before, the ``socache_shmcb``
  module was implicitly loaded by the ``ssl`` module. [ypid_]

- Fix ``item.https_enabled`` support for virtual hosts. This variable was
  ignored previously using the global default (``True``) directly. [ypid_]
