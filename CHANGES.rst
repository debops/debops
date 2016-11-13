.. _secret__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.secret**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.secret master`_ - unreleased
------------------------------------

.. _debops.secret master: https://github.com/debops/ansible-secret/compare/v0.2.3...master

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]


`debops.secret v0.2.3`_ - 2016-01-04
------------------------------------

.. _debops.secret v0.2.3: https://github.com/debops/ansible-secret/compare/v0.2.2...v0.2.3

Added
~~~~~

- Add ``secret_directories`` list which can be used to create directories on
  Ansible Controller inside :file:`secret/` directory for other roles to use.
  [drybjed_]

Changed
~~~~~~~

- Rename ``secret_dir`` variable to ``secret_name`` to avoid ambiguity.
  [drybjed_]


`debops.secret v0.2.2`_ - 2015-09-23
------------------------------------

.. _debops.secret v0.2.2: https://github.com/debops/ansible-secret/compare/v0.2.1...v0.2.2

Added
~~~~~

- Add ``secret_ldap_services_dn``. [scibi_]


`debops.secret v0.2.1`_ - 2015-02-25
------------------------------------

.. _debops.secret v0.2.1: https://github.com/debops/ansible-secret/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Redesign LDAP support, add more required variables. [drybjed_]


`debops.secret v0.2.0`_ - 2015-02-24
------------------------------------

.. _debops.secret v0.2.0: https://github.com/debops/ansible-secret/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add LDAP integration. [drybjed_]

Changed
~~~~~~~

- Convert documentation to new format. [drybjed_]


debops.secret v0.1.0 - 2015-02-12
---------------------------------

Added
~~~~~

- First release, add CHANGES.rst. [drybjed_]
