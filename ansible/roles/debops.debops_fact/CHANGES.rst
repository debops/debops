Changelog
=========

.. include:: includes/all.rst

**debops.debops_fact**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.debops_fact master`_ - unreleased
-----------------------------------------

.. _debops.debops_fact master: https://github.com/debops/ansible-debops_fact/compare/v0.2.1...master


`debops.debops_fact v0.2.1`_ - 2016-11-13
-----------------------------------------

.. _debops.debops_fact v0.2.1: https://github.com/debops/ansible-debops_fact/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- The role now expects a valid INI file with section headers.
  It does not patch in a ``[default]`` section when the file is missing one and
  will instead raise an exception. [ypid_]

Fixed
~~~~~

- Problem where the :file:`/etc/ansible/facts.d/debops_fact.fact` file would
  fail to return facts and throw a Python exception instead. [ypid_]


`debops.debops_fact v0.2.0`_ - 2016-09-13
-----------------------------------------

.. _debops.debops_fact v0.2.0: https://github.com/debops/ansible-debops_fact/compare/v0.1.2...v0.2.0

Added
~~~~~

- Add a way to disable support for DebOps facts if desired. [drybjed_]

Changed
~~~~~~~

- Redesign the DebOps fact storage and switch from the JSON files stored
  directly as Ansible local facts to separate INI files that hold the JSON data
  in the variable values. This allows modification of the INI files directly by
  other roles using ``ini_file`` Ansible module and the role itself doesn't
  need to be involved in the process. [drybjed_]

Removed
~~~~~~~

- The ``debops_fact__*_facts`` variables which allowed to set custom facts via
  inventory or role dependent variables are removed; roles can modify the INI
  files directly now. [drybjed_]


`debops.debops_fact v0.1.2`_ - 2016-09-01
-----------------------------------------

.. _debops.debops_fact v0.1.2: https://github.com/debops/ansible-debops_fact/compare/v0.1.1...v0.1.2

Removed
~~~~~~~

- Ansible does not work with local facts that are unreadable by unprivileged
  users. A different solution for private local facts will be written later.
  [drybjed_]


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
