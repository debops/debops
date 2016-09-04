.. _redis__ref_changelog:

Changelog
=========

**debops.redis**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.redis master`_ - unreleased
-----------------------------------

.. _debops.redis master: https://github.com/debops/ansible-redis/compare/v0.1.0...master

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
