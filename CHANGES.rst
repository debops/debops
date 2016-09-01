Changelog
=========

.. include:: includes/all.rst

**debops.debops_fact**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.debops_fact master`_ - unreleased
-----------------------------------------

.. _debops.debops_fact master: https://github.com/debops/ansible-debops_fact/compare/v0.1.2...master


`debops.debops_fact v0.1.2`_ - 2016-09-01
-----------------------------------------

.. _debops.debops_fact v0.1.2: https://github.com/debops/ansible-debops_fact/compare/v0.1.1...v0.1.2

Removed
~~~~~~~

- Ansible does not work with local facts that are unreadable by unprivileged
  users. A different solution for private local facts will be written later.
  [drybjed]


`debops.debops_fact v0.1.1`_ - 2016-08-07
-----------------------------------------

.. _debops.debops_fact v0.1.1: https://github.com/debops/ansible-debops_fact/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Move redundant template code to a shared macro. [drybjed_]


debops.debops_fact v0.1.0 - 2016-08-07
--------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
