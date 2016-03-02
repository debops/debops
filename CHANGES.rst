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

- Rewrite the language pack support.

  The role now exposes simple list of languages which is converted by a lookup
  template to set the ``debconf`` questions correctly. List of active languages
  is taken into account, so both data sources (Ansible default variables and
  ``debconf`` database) shouldn't fight over which languages are active
  anymore.

  The language pack conversion script has been rewritten to be idempotent and
  it's not installed on the remote host, but executed by the ``script`` module
  if any changes are detected. [drybjed]

- Drop Ansible local facts related to Mailman. [drybjed]

- Redesign the configuration of Mailman domains. The default domain is now set
  in a separate ``mailman__site_domain`` variable, and additional virtual
  domains have their own list. [drybjed]

- Clean up role tasks and handlers, conver them to YAML syntax. [drybjed]

