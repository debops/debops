Changelog
=========

**debops.tcpwrappers**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.tcpwrappers master`_ - unreleased
-----------------------------------------

.. _debops.tcpwrappers master: https://github.com/debops/ansible-tcpwrappers/compare/v0.2.2...master


`debops.tcpwrappers v0.2.2`_ - 2016-10-10
-----------------------------------------

.. _debops.tcpwrappers v0.2.2: https://github.com/debops/ansible-tcpwrappers/compare/v0.2.1...v0.2.2

Fixed
~~~~~

- Make sure that the ``accept_any`` parameter correctly enables or disables
  entries. [drybjed]


`debops.tcpwrappers v0.2.1`_ - 2016-08-07
-----------------------------------------

.. _debops.tcpwrappers v0.2.1: https://github.com/debops/ansible-tcpwrappers/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Make sure that ``/etc/hosts.deny`` file exists. [drybjed]

- Update documentation and Changelog. [drybjed]


`debops.tcpwrappers v0.2.0`_ - 2016-05-27
-----------------------------------------

.. _debops.tcpwrappers v0.2.0: https://github.com/debops/ansible-tcpwrappers/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Role has been cleaned up and documented. The default variables have been
  renamed from ``tcpwrappers_`` to ``tcpwrappers__`` to indicate the separate
  namespace (some of the old variables are still supported). Some of the old
  configuration parameters like ``item.enabled`` or ``item.disabled`` have been
  removed and ``item.state`` is used to control the configuration state.
  [drybjed]


debops.tcpwrappers v0.1.0 - 2016-02-08
--------------------------------------

Added
~~~~~

- Add Changelog. [drybjed]

Changed
~~~~~~~

- Rename the ``tcpwrappers`` variable to ``tcpwrappers_enabled`` and clean up
  of some tasks to use YAML format. [drybjed]

- Move a variable from ``vars/main.yml`` to ``defaults/main.yml``. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Small clean up of logic in templates, add support for ``debops.core``
  ``ansible_controllers`` variable. [drybjed]
