Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Remove hard role dependencies on ``debops.postfix`` and ``debops.nginx``.
  Configuration for ``debops.postfix`` and ``debops.nginx`` roles is defined in
  default variables, which can be passed to the roles through the playbook.

  Remove direct configuration of ``fcgiwrap`` instance and use
  ``debops.fcgiwrap`` role to configure a ``mailman`` instance. [drybjed]

