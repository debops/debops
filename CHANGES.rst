Changelog
=========

**debops.librenms**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.librenms master`_ - unreleased
--------------------------------------

.. _debops.librenms master: https://github.com/debops/ansible-librenms/compare/v0.1.1...master

Changed
~~~~~~~

- Updated documentation and Changelog. [drybjed]

- Move the role dependent variables to ``defaults/main.yml`` file and remove
  the role dependencies from ``meta/main.yml``. They are moved to the playbook
  instead. [drybjed]

Fixed
~~~~~

- Fix empty default admin account on Ansible v2. [drybjed]

- Switch to list of admin accounts from ``debops.core`` role. [drybjed]

- Fix Ansible deprecation warnings. [drybjed]


`debops.librenms v0.1.1`_ - 2015-09-25
--------------------------------------

.. _debops.librenms v0.1.1: https://github.com/debops/ansible-librenms/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Don't update the LibreNMS installation during Ansible runs, it takes of that
  itself by a script that can handle database changes. [drybjed]

- Update LibreNMS ``cron`` entries. [drybjed]


debops.librenms v0.1.0 - 2015-08-07
-----------------------------------

Added
~~~~~

- Initial release. [drybjed]
