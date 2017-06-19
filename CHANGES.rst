.. _redis__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.redis**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.redis master`_ - unreleased
-----------------------------------

.. _debops.redis master: https://github.com/debops/ansible-redis/compare/v0.2.1...master

Added
~~~~~

- Enable memory overcommit by default. Redis is not able to fork to make
  a background save if it uses more than half of the available memory with
  overcommit disabled. [scibi_]

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


`debops.redis v0.2.1`_ - 2016-11-18
-----------------------------------

.. _debops.redis v0.2.1: https://github.com/debops/ansible-redis/compare/v0.2.0...v0.2.1

Added
~~~~~

- Expose current Redis version in Ansible facts. [ypid_]

Fixed
-----

- Reviewed the role. Fixed potential shell script issues reported by
  :command:`shellcheck` and added CI tests using :command:`shellcheck`.
  Note that the script is checked after being templated by Jinja which might
  not cover all code paths.  [ypid_]

- Fix an issue on Ansible 2.2 where some dictionary keys are undefined due to
  a legitimately skipped tasks. [drybjed_]

- Make sure that the fact script does not fail when Redis service cannot be
  reached. [drybjed_]


`debops.redis v0.2.0`_ - 2016-09-08
-----------------------------------

.. _debops.redis v0.2.0: https://github.com/debops/ansible-redis/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- Move the role variables from :file:`vars/main.yml` to :file:`defaults/main.yml`.
  [drybjed_]

- The role has been redesigned from the ground up. Variables and service
  parameters have been reorganized, role supports standalone as well as
  clustered operation with Redis Sentinel. [drybjed_]


debops.redis v0.1.0 - 2016-06-28
--------------------------------

Added
~~~~~

- First release. [drybjed_]
