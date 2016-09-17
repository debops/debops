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

.. _debops.redis master: https://github.com/debops/ansible-redis/compare/v0.2.0...master

Fixed
-----

- Reviewed the role. Fixed potential shell script issues reported by
  ``shellcheck`` and added CI tests using ``shellcheck``.
  Note that the script is checked after being templated by Jinja which might
  not cover all code paths.  [ypid_]


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
