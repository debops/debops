Changelog
=========

v0.1.3
------

**Haste makes waste.**

*Released: 2016-02-24*

- Remove not used handlers. [drybjed]

- Fix missing paren in the ``systemd`` socket unit. [drybjed]

v0.1.2
------

*Released: 2016-02-24*

- Move the list of APT packages to defaults. [drybjed]

- Disable default ``fcgiwrap`` service on both ``systemd`` and ``sysvinit``
  systems. [drybjed]

- Don't recreate new default ``systemd`` units to replace the ones in
  ``/lib/systemd/``. The role is focused on managing multiple ``fcgiwrap``
  instances and not the default one. [drybjed]

- Move user management tasks to ``tasks/main.yml``. [drybjed]

- Fix deprecation warnings on Ansible 2.1.0. [drybjed]

- Clean up ``when`` conditions. [drybjed]

- Rename all variables from ``fcgiwrap_*`` to ``fcgiwrap__*``. [drybjed]

v0.1.1
------

*Released: 2015-09-01*

- Update the execution conditions of included tasks to run tasks managing the
  default ``fcgiwrap`` instance even when list of instances is empty. [drybjed]

- Fix the Debian issue where init scripts interfere with ``systemd`` units.
  Role will create proper ``systemd`` units for default ``fcgiwrap`` instance
  which will mask the init script and will be correctly disabled without any
  idempotency issues. [drybjed]

v0.1.0
------

*Released: 2015-08-30*

- Initial release. [drybjed]

