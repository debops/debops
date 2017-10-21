Changelog
=========

.. include:: includes/all.rst

**debops.grub**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.grub master`_ - unreleased
----------------------------------

.. _debops.grub master: https://github.com/debops/ansible-grub/compare/v0.1.2...master

Added
~~~~~

- Remove password protection if no users are defined. [ypid_]

Changed
~~~~~~~

- Updated example playbook and inventory in the documentation. [ypid_]

- Update to min Ansible version to 2.1.4'. [ypid_]

Fixed
~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [ypid_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Fix password protection feature which was broken with Ansible 2.1 and above
  because of changes how ``\n`` is handled by Jinja. [Polichronucci, ypid_]


`debops.grub v0.1.2`_ - 2015-10-23
----------------------------------

.. _debops.grub v0.1.2: https://github.com/debops/ansible-grub/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Make sure that role works in Ansible check mode. [drybjed_]

Fixed
~~~~~

- Change the way role gathers default and old kernel parameters to avoid issues
  with ``sed`` in Ansible v2. [drybjed_]


`debops.grub v0.1.1`_ - 2015-09-02
----------------------------------

.. _debops.grub v0.1.1: https://github.com/debops/ansible-grub/compare/v0.1.0...v0.1.1

Fixed
~~~~~

- Fix an issue with undefined variable. [scibi_]


debops.grub v0.1.0 - 2015-09-01
-------------------------------

Added
~~~~~

- First release. [scibi_, drybjed_]
