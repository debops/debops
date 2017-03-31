.. _dropbear_initramfs__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops-contrib.dropbear_initramfs**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.

Refer to the :ref:`dropbear_initramfs__ref_upgrade_nodes` when you intend to
upgrade to a new release.


`debops-contrib.dropbear_initramfs master`_ - unreleased
--------------------------------------------------------

.. _debops-contrib.dropbear_initramfs master: https://github.com/debops-contrib/ansible-dropbear_initramfs/compare/v0.2.0...master


`debops-contrib.dropbear_initramfs v0.2.0`_ - 2017-03-31
--------------------------------------------------------

.. _debops-contrib.dropbear_initramfs v0.2.0: https://github.com/debops-contrib/ansible-dropbear_initramfs/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add IPv6 support. [ypid_]

Changed
~~~~~~~

- Rename role to ``debops-contrib.dropbear_initramfs``. [ypid_]

- Changed license from AGPL-3.0 to GPL-3.0. [ypid_]

- Major rewrite which breaks backwards compatibility and legacy support.
  Refer to :ref:`dropbear_initramfs__ref_upgrade_nodes_v0.2.0` for details.
  [ypid_]

- Require Ansible version 2.1.4 or above. [ypid_]


ypid.cryptsetup_remote_unlock v0.1.0 - 2016-07-18
-------------------------------------------------

Added
~~~~~

- Initial coding and design. Dates back to 2015-03-01. [ypid_]
