Changelog
=========

v0.2.0
------

*Unreleased*

- Wrote documentation. [ypid]

- Reworked role, updated metadata. [ypid]

- Renamed ``etc_services`` to ``etc_services__enabled``. [ypid]

- Renamed ``etc_services_([^_].+)`` to ``etc_services__\1``.
  Old list variables are deprecated but still work for now. [ypid]

- Change the task conditions to test for boolean values instead of only
  checking if a variable is defined. [drybjed]

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Support custom service definitions. [drybjed]

