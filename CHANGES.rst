Changelog
=========

**debops.core**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.core master`_ - unreleased
----------------------------------

.. _debops.core master: https://github.com/debops/ansible-core/compare/v0.2.0...master

Added
~~~~~

- Add list of system administrator groups and user accounts exposed as local
  Ansible facts. This can be used by other roles to automatically create admin
  accounts in services. [drybjed]

- Add ``cache`` and ``spool`` directories to list of common directories used by
  roles. They point to ``/var/cache`` and ``/var/spool`` directories by
  default. [drybjed]

Changed
~~~~~~~

- The ``core.fact`` has been changed from a static file to a Python script to
  make it more dynamic. [drybjed]


`debops.core v0.2.0`_ - 2016-07-19
----------------------------------

.. _debops.core v0.2.0: https://github.com/debops/ansible-core/compare/v0.1.4...v0.2.0

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed]

- Rename all role variables from ``core_*`` to ``core__*`` to move them into
  their own namespace. [drybjed]


`debops.core v0.1.4`_ - 2016-02-08
----------------------------------

.. _debops.core v0.1.4: https://github.com/debops/ansible-core/compare/v0.1.3...v0.1.4

Added
~~~~~

- Add a note about IP addresses of Ansible Controller and ``become`` setting in
  inventory. [drybjed]

Fixed
~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]


`debops.core v0.1.3`_ - 2015-12-17
----------------------------------

.. _debops.core v0.1.3: https://github.com/debops/ansible-core/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Gather local facts if they changed, in case the role is used in a play with
  other roles. [drybjed]


`debops.core v0.1.2`_ - 2015-10-19
----------------------------------

.. _debops.core v0.1.2: https://github.com/debops/ansible-core/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add a ``core_active_controller`` variable which specifies IP address of
  active Ansible Controller. [drybjed]


`debops.core v0.1.1`_ - 2015-08-22
----------------------------------

.. _debops.core v0.1.1: https://github.com/debops/ansible-core/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add script to gather information from ``/etc/resolv.conf``, available in the
  Ansible Facts as ``ansible_local.resolver.*``. [drybjed]

debops.core v0.1.0 - 2015-08-22
-------------------------------

Added
~~~~~

- Initial release. [drybjed]
