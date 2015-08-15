Changelog
=========

v0.2.0
------

*Unreleased*

- Remove ``tasks/backup.yml`` and ``tasks/restore.yml``, they are not used in
  main role task list. [drybjed]

- Request ``sudo`` access on Travis-CI. [drybjed]

- Update documentation. [drybjed]

- Remove ``debops.auth`` role dependency. Configuration done by this role is
  assumed to be present, since it's executed as part of the ``common.yml``
  playbook. [drybjed]

v0.1.0
------

*Released: 2015-08-10*

- Add Changelog. [drybjed]

