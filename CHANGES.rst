Changelog
=========

v0.1.2
------

*Released: 2016-02-24*

- Move the list of APT packages to defaults. [drybjed]

- Disable default ``fcgiwrap`` service on both ``systemd`` and ``sysvinit``
  systems. [drybjed]

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

