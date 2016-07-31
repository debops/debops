Changelog
=========

**debops.debops**

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.debops master`_ - unreleased
------------------------------------

.. _debops.debops master: https://github.com/debops/ansible-debops/compare/v0.2.1...master

Fixed
~~~~~

- Fix sudo behaviour when ``debops__install_systemwide`` is enabled. [ganto]

- Don't trigger role update handler when ``debops__update_method`` is sync. [ganto]


`debops.debops v0.2.1`_ - 2016-07-14
------------------------------------

.. _debops.debops v0.2.1: https://github.com/debops/ansible-debops/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add support for installing Ansible from ``git`` source using a bootstrap script. [drybjed]

Fixed
~~~~~

- Rename forgotten variable names in handlers. [drybjed]


`debops.debops v0.2.0`_ - 2016-07-13
------------------------------------

.. _debops.debops v0.2.0: https://github.com/debops/ansible-debops/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add support for Ansible installation from Debian Backports. [ganto]

- Add support for cloning or initializing a new DebOps project. [ganto]

- Add update method 'sync' for roles and playbooks. [ganto]

Changed
~~~~~~~

- Change variable prefix from ``debops_`` to ``debops__``. [ganto]

- Fix DebOps installation for local user. [ganto]


debops.debops v0.1.0 - 2015-10-28
---------------------------------

Added
~~~~~

- Add Changelog. [drybjed]

Changed
~~~~~~~

- Rewrite the role to install ``debops`` package from PyPI instead of cloned
  repository. [drybjed]

- Install DebOps playbooks and roles in the background using handlers.
  [drybjed]

- Update documentation. [drybjed]
