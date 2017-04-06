.. _apt_cacher_ng__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.apt_cacher_ng**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


`debops.apt_cacher_ng master`_ - unreleased
-------------------------------------------

.. _debops.apt_cacher_ng master: https://github.com/debops/ansible-apt_cacher_ng/compare/v0.2.1...master

Fixed
~~~~~

- In Jessie, the backported ``apt-cacher-ng`` package now also requires a
  backported ``libssl1.0.0`` package (and ``libssl-dev``, in case that is
  installed). Update the APT pinning accordingly so that it is ensured that the
  package is upgraded correctly and not kept back.
  It might depend on your global APT pinning configuration if the package would
  have been kept back without this or not. [ypid_]


`debops.apt_cacher_ng v0.2.2`_ - 2017-03-29
-------------------------------------------

.. _debops.apt_cacher_ng v0.2.2: https://github.com/debops/ansible-apt_cacher_ng/compare/v0.2.1...v0.2.2

Fixed
~~~~~

- Fix regression in the Debian upstream mirror selection introduced in v0.2.1.
  When the role was run against a non-Debian host then a mirror for another distribution
  might have been selected as Debian mirror. [ypid_]


`debops.apt_cacher_ng v0.2.1`_ - 2017-03-27
-------------------------------------------

.. _debops.apt_cacher_ng v0.2.1: https://github.com/debops/ansible-apt_cacher_ng/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Use the default APT mirror set by debops.apt_ or fallback to the official Debian
  repository source at ``http://deb.debian.org/debian`` due to `the deprecation
  of the httpredir service <https://lists.debian.org/debian-mirrors/2017/02/msg00000.html>`_.
  [ypid_]


`debops.apt_cacher_ng v0.2.0`_ - 2016-10-23
-------------------------------------------

.. _debops.apt_cacher_ng v0.2.0: https://github.com/debops/ansible-apt_cacher_ng/compare/v0.1.0...v0.2.0

Added
~~~~~

- Added support for AppArmor. Refer to :ref:`apt_cacher_ng__ref_getting_started`
  for details. [ypid_]

- Added :envvar:`apt_cacher_ng__connect_protocol` to allow to specify which IP
  version to prefer when contacting upstream mirrors. [ypid_]

- Added :envvar:`apt_cacher_ng__interfaces` for restricting access to
  connections through that interface by the firewall. [ypid_]

Changed
~~~~~~~

- Don’t ensure that the latest version of the :envvar:`apt_cacher_ng__base_packages`
  is installed on subsequent role runs. [ypid_]

- Renamed variables to be consistent with DebOps:

  +-------------------------------------------+-------------------------------------------+
  | Old variable                              | New variable                              |
  +===========================================+===========================================+
  | ``apt_cacher_ng__nginx_upstream``         | :envvar:`apt_cacher_ng__nginx__upstream`  |
  +-------------------------------------------+-------------------------------------------+
  | ``apt_cacher_ng__nginx_upstream_servers`` | :envvar:`apt_cacher_ng__upstream_servers` |
  +-------------------------------------------+-------------------------------------------+

  The role bundles a script which can do this transition for you.
  Refer to :ref:`apt_cacher_ng__ref_upgrade_nodes_v0.2.0` for details. [ypid_]

- Updated to latest DebOps Standards. [ypid_]

- Use the `Ansible package module`_ which requires Ansible v2.0. [ypid_]


debops.apt_cacher_ng v0.1.0 - 2016-03-22
----------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Add support for proxying the Apt-Cacher NG server via :program:`nginx` on
  a subdomain. Direct access to the cache is still possible. [drybjed_]

Changed
~~~~~~~

- Switch the default Debian mirror to new official redirector at
  http://httpredir.debian.org/. [ypid_]

- Enable installation of backported :program:`apt-cacher-ng` package on Debian Wheezy.
  [drybjed_]

- Check boolean values in configuration template. [drybjed_]
