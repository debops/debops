Changelog
=========

.. include:: includes/all.rst

**debops.persistent_paths**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


`debops.persistent_paths master`_ - unreleased
----------------------------------------------

.. _debops.persistent_paths master: https://github.com/debops/ansible-persistent_paths/compare/v0.1.0...master

Added
~~~~~

- Add ``role::persistent_paths:qubes_os`` Ansible tag for Qubes OS related tasks. [ypid_]

- Add Ansible facts. [ypid_]

- Document procedure needed to update/change persistent files on Qubes OS in
  :ref:`persistent_paths__ref_guide_updating_persistent_files`. [ypid_, drybjed_]

Changed
~~~~~~~

- Rename ``persistent_paths__qubes_os_paths`` to
  :envvar:`persistent_paths__qubes_os_default_persistent_paths`. [ypid_]

- Rename ``persistent_paths__qubes_os_bind_dirs`` to
  :envvar:`persistent_paths__qubes_os_handler`. [ypid_]


debops.persistent_paths v0.1.0 - 2017-02-03
-------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]
