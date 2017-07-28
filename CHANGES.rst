Changelog
=========

**debops.debops**

.. include:: includes/all.rst

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.debops master`_ - unreleased
------------------------------------

.. _debops.debops master: https://github.com/debops/ansible-debops/compare/v0.2.3...master

Fixed
~~~~~

- Add ``python-crypto`` package to requirements for Ansible from source. [ganto_]


`debops.debops v0.2.3`_ - 2017-02-12
------------------------------------

.. _debops.debops v0.2.3: https://github.com/debops/ansible-debops/compare/v0.2.2...v0.2.3

Added
~~~~~

- Add ``python-sphinx`` package to requirements for Ansible from source. [drybjed_]

Changed
~~~~~~~

- Support newer Ansible local build methos using ``local_deb``. [drybjed_]


`debops.debops v0.2.2`_ - 2016-07-31
------------------------------------

.. _debops.debops v0.2.2: https://github.com/debops/ansible-debops/compare/v0.2.1...v0.2.2

Fixed
~~~~~

- Fix sudo behaviour when :envvar:`debops__install_systemwide` is enabled. [ganto_]

- Don't trigger role update handler when :envvar:`debops__update_method` is sync. [ganto_]

- Only install system-wide ``debops.cfg`` if requested. [ganto_]

- Update documentation. [drybjed_]


`debops.debops v0.2.1`_ - 2016-07-14
------------------------------------

.. _debops.debops v0.2.1: https://github.com/debops/ansible-debops/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add support for installing Ansible from :command:`git` source using a bootstrap script. [drybjed_]

Fixed
~~~~~

- Rename forgotten variable names in handlers. [drybjed_]


`debops.debops v0.2.0`_ - 2016-07-13
------------------------------------

.. _debops.debops v0.2.0: https://github.com/debops/ansible-debops/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add support for Ansible installation from Debian Backports. [ganto_]

- Add support for cloning or initializing a new DebOps project. [ganto_]

- Add update method 'sync' for roles and playbooks. [ganto_]

Changed
~~~~~~~

- Change variable prefix from ``debops_`` to ``debops__``. [ganto_]

- Fix DebOps installation for local user. [ganto_]


debops.debops v0.1.0 - 2015-10-28
---------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

Changed
~~~~~~~

- Rewrite the role to install ``debops`` package from PyPI instead of cloned
  repository. [drybjed_]

- Install DebOps playbooks and roles in the background using handlers.
  [drybjed_]

- Update documentation. [drybjed_]
