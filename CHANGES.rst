Changelog
=========

.. include:: includes/all.rst

**debops.swapfile**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_


`debops.swapfile master`_ - unreleased
----------------------------------------

.. _debops.swapfile master: https://github.com/debops/ansible-swapfile/compare/v0.2.0...master

Added
~~~~~

- Add support for Ansible check mode. This requires Ansible v2.1 which is thus
  became the minimum requirement to run the role. [ypid_]

Changed
~~~~~~~

- Update the role to the latest DebOps Standards. [ypid_]


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
