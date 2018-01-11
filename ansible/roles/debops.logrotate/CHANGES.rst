Changelog
=========

.. include:: includes/all.rst

**debops.logrotate**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_


`debops.logrotate master`_ - unreleased
---------------------------------------

.. _debops.logrotate master: https://github.com/debops/ansible-logrotate/compare/v0.1.2...master

Changed
~~~~~~~

- Mostly automated update to the latest DebOps Standards Version. [ypid_]

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


`debops.logrotate v0.1.2`_ - 2016-07-05
---------------------------------------

.. _debops.logrotate v0.1.2: https://github.com/debops/ansible-logrotate/compare/v0.1.1...v0.1.2

Fixed
~~~~~

- Role will now correctly divert/revert ``logrotate`` configuration files for
  packages that are not yet installed. This fixes an issue where specified file
  not present in the filesystem was diverted on each run, breaking idempotency.
  [drybjed_]


`debops.logrotate v0.1.1`_ - 2016-05-18
---------------------------------------

.. _debops.logrotate v0.1.1: https://github.com/debops/ansible-logrotate/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Allow configuration of ``logrotate`` options common to all logs when no
  specific logs are set. [drybjed_]


debops.logrotate v0.1.0 - 2016-04-15
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
