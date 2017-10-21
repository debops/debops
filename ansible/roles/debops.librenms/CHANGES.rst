Changelog
=========

**debops.librenms**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.librenms master`_ - unreleased
--------------------------------------

.. _debops.librenms master: https://github.com/debops/ansible-librenms/compare/v0.2.0...master


`debops.librenms v0.2.0`_ - 2016-08-14
--------------------------------------

.. _debops.librenms v0.2.0: https://github.com/debops/ansible-librenms/compare/v0.1.1...v0.2.0

Added
~~~~~

- Add ``librenms__fqdn`` variable to better indicate the meaning of what should
  be in it and use it in the ``nginx`` configuration to set the name of the
  LibreNMS web page. [drybjed]

Changed
~~~~~~~

- Updated documentation and Changelog. [drybjed]

- Move the role dependent variables to ``defaults/main.yml`` file and remove
  the role dependencies from ``meta/main.yml``. They are moved to the playbook
  instead. [drybjed]

- Rename all variables from ``librenms_*`` to ``librenms__*`` to move them to
  their own namespace. You will need to update your inventory. [drybjed]

- Move the ``logrotate`` configuration to ``debops.logrotate`` role included in
  the playbook. [drybjed]

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
