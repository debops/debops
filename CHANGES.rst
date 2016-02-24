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

- Switch from patching the Mailman source code manually to using the ``patch``
  Ansible module. Patches are no longer copied to remote host and their state
  is not stored on the server, however it's easy to apply them again if
  necessary using a dedicated tag. [drybjed]

- Perform UTF-8 conversion of Polish language pack only on Debian Wheezy and
  Ubuntu Precise, newer OS releases should be fine. [drybjed]

- Restart Mailman on configuration changes. [drybjed]

- Clean up APT package installation, expose list of packages in default
  variables. [drybjed]

