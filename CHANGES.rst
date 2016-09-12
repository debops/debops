Changelog
=========

**debops.core**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer is drybjed.


`debops.core master`_ - unreleased
----------------------------------

.. _debops.core master: https://github.com/debops/ansible-core/compare/v0.2.4...master


`debops.core v0.2.4`_ - 2016-09-12
----------------------------------

.. _debops.core v0.2.4: https://github.com/debops/ansible-core/compare/v0.2.3...v0.2.4

Added
~~~~~

- Add lists of public and private system administrator email addresses, usable
  by other roles through Ansible local facts. [drybjed]


`debops.core v0.2.3`_ - 2016-08-29
----------------------------------

.. _debops.core v0.2.3: https://github.com/debops/ansible-core/compare/v0.2.2...v0.2.3

Added
~~~~~

- Add custom local facts that define OS distribution and release. [drybjed]


`debops.core v0.2.2`_ - 2016-08-14
----------------------------------

.. _debops.core v0.2.2: https://github.com/debops/ansible-core/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- The ``core.fact`` Python script now parses JSON Ansible output instead of
  setting it in a variable directly. [drybjed]

- Refactor ``admin_users`` variable in the ``core.fact`` Python script.
  [drybjed]


`debops.core v0.2.1`_ - 2016-08-13
----------------------------------

.. _debops.core v0.2.1: https://github.com/debops/ansible-core/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add list of system administrator groups and user accounts exposed as local
  Ansible facts. This can be used by other roles to automatically create admin
  accounts in services. [drybjed]

- Add ``cache`` and ``spool`` directories to list of common directories used by
  roles. They point to ``/var/cache`` and ``/var/spool`` directories by
  default. [drybjed]

- The ``debops_service_core`` inventory group can be used to enable the
  ``debops.core`` role without the rest of the playbook. [drybjed]

- Add facts for the host domain and FQDN. This will allow for a centralized
  configuration of these parameters in the future for roles that use them.
  [drybjed]

Changed
~~~~~~~

- The ``core.fact`` has been changed from a static file to a Python script to
  make it more dynamic. [drybjed]

- Move the ``apt`` installation task to the top of the task list and change it
  to the ``package`` module to make the role more portable. Role will not
  update the package list anymore, but it's expected to be done by the
  bootstrapping infrastructure before the first playbook execution. [drybjed]


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
