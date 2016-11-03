Changelog
=========

v0.3.0
------

*Released: 2016-04-25*

- Added ``delete`` boolean switch to allow to delete local services. [ypid_]

- Condense the :command:`dpkg-divert` revert tasks into one. [drybjed_]

- Add support for ``item.state`` parameter. [drybjed_]

v0.2.0
------

*Released: 2016-03-14*

- Wrote documentation. [ypid_]

- Reworked role, updated metadata. [ypid_]

- Renamed ``etc_services`` to :envvar:`etc_services__enabled`. [ypid_]

- Renamed ``etc_services_([^_].+)`` to ``etc_services__\1``.
  Old list variables are deprecated but still work for now. [ypid_]

- Change the task conditions to test for boolean values instead of only
  checking if a variable is defined. [drybjed_]

v0.1.0
------

*Released: 2016-03-14*

- Add Changelog. [drybjed_]

- Support custom service definitions. [drybjed_]

