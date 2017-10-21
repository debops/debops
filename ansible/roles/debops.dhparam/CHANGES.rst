.. _dhparam__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.dhparam**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.dhparam master`_ - unreleased
-------------------------------------

.. _debops.dhparam master: https://github.com/debops/ansible-dhparam/compare/v0.1.2...master

Added
~~~~~

- Add  :envvar:`dhparam__deploy_state` to allow to specify the desired state this
  role should achieve. State ``absent`` is not fully implemented yet. [ypid_]

- Add 2048 bits size in :envvar:`dhparam__bits` in order to use it in nginx servers
  accessed by OpenJDK 8 clients. [pedroluislopez_]

Changed
~~~~~~~

- Update the role to DebOps Standards v0.2.1. [ypid_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


`debops.dhparam v0.1.2`_ - 2016-02-23
-------------------------------------

.. _debops.dhparam v0.1.2: https://github.com/debops/ansible-dhparam/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Move the list of APT packages to a default variable, install :program:`cron` package
  when necessary. [drybjed_]

- Rename all role variables from ``dhparam_*`` to ``dhparam__*`` to move them
  to their own namespace. [drybjed_]

Fixed
~~~~~

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]


`debops.dhparam v0.1.1`_ - 2015-11-24
-------------------------------------

.. _debops.dhparam v0.1.1: https://github.com/debops/ansible-dhparam/compare/v0.1.0...v0.1.1

Added
~~~~~

- Support Ansible check mode. [drybjed_]


debops.dhparam v0.1.0 - 2015-10-22
----------------------------------

Added
~~~~~

- Initial release. [drybjed_]

Changed
~~~~~~~

- Reviewed and fixed spelling. [ypid_]
