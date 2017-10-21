.. _swapfile__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.swapfile**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.swapfile master`_ - unreleased
----------------------------------------

.. _debops.swapfile master: https://github.com/debops/ansible-swapfile/compare/v0.2.0...master

Added
~~~~~

- Add :ref:`swapfile__ref_upgrade_nodes`. [ypid_]

Removed
~~~~~~~

- Management of kernel parameters is now handled by debops.sysctl_.
  The related variables like ``swapfile__swappiness`` and
  ``swapfile__cache_pressure`` have no effect anymore.
  Refer to :ref:`swapfile__ref_upgrade_nodes_v0.4.0` for details.
  [ypid_]

- Remove deprecated Ansible inventory group ``debops_service_swapfile``. Refer
  to the :ref:`swapfile__ref_getting_started` guide. [ypid_]


`debops.swapfile v0.3.0`_ - 2016-10-29
--------------------------------------

.. _debops.swapfile v0.3.0: https://github.com/debops/ansible-swapfile/compare/v0.2.0...v0.3.0

Added
~~~~~

- Add support for Ansible check mode. This requires Ansible v2.1 which thus
  became the minimum requirement to run the role. [ypid_]

Changed
~~~~~~~

- Update the role to the latest DebOps Standards. [ypid_]

- Remove the swap file after removing the entry from :file:`/etc/fstab` for the
  case when the role run is aborted in the middle. [ypid_]


`debops.swapfile v0.2.0`_ - 2016-04-04
--------------------------------------

.. _debops.swapfile v0.2.0: https://github.com/debops/ansible-swapfile/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Update the swapfile size parameter to be more dynamic and create bigger swap
  files if system has small amount of RAM available. [drybjed_]

- Rename all variables to put them in separate namespace. [drybjed_]


debops.swapfile v0.1.0 - 2015-10-16
-----------------------------------

Added
~~~~~

- Initial release. [drybjed_]
