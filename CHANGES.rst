.. _nfs__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.nfs**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.nfs master`_ - unreleased
---------------------------------

.. _debops.nfs master: https://github.com/debops/ansible-nfs/compare/v0.2.2...master


`debops.nfs v0.2.2`_ - 2017-04-10
---------------------------------

.. _debops.nfs v0.2.2: https://github.com/debops/ansible-nfs/compare/v0.2.1...v0.2.2

Added
~~~~~

- Allow configuration of directory owner, group and permissions for NFS shares
  that are not mounted immediately by the role. [drybjed_]


`debops.nfs v0.2.1`_ - 2017-04-07
---------------------------------

.. _debops.nfs v0.2.1: https://github.com/debops/ansible-nfs/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- If the Kerberos is not enabled, role will now default to the ``sec=sys``
  mount option. This is done to ensure that even on Kerberos-enabled systems
  mount points which shouldn't use Kerberos behave correctly. [drybjed_]

Fixed
~~~~~

- Ensure that the ``item.state`` parameter has a default state in condition.
  [drybjed_]


`debops.nfs v0.2.0`_ - 2017-04-05
---------------------------------

.. _debops.nfs v0.2.0: https://github.com/debops/ansible-nfs/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- The role has been completely rewritten and split into two roles. The NFS
  server part has been moved to the new ``debops.nfs_server`` Ansible role, and
  this role now manages the client-side NFS configuration. The variables have
  been renamed, therefore you will need to update your inventory. Make sure
  that you test the new roles before deploying them in production environment.
  [drybjed_]


debops.nfs v0.1.0 - 2015-03-02
------------------------------

Added
~~~~~

- Initial release [drybjed_]
