Changelog
=========

.. include:: includes/all.rst

**debops.mailman**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.mailman master`_ - unreleased
-------------------------------------

.. _debops.mailman master: https://github.com/debops/ansible-mailman/compare/v0.2.0...master


`debops.mailman v0.2.0`_ - 2017-09-04
-------------------------------------

.. _debops.mailman v0.2.0: https://github.com/debops/ansible-mailman/compare/v0.1.3...v0.2.0

Added
~~~~~

- Add the Ansible local fact that indicates that the Mailman has been installed
  on a host. [drybjed_]

Changed
~~~~~~~

- Update the Postfix integration to support the rewritten debops.postfix_
  Ansible role. [drybjed_]


`debops.mailman v0.1.3`_ - 2016-07-18
-------------------------------------

.. _debops.mailman v0.1.3: https://github.com/debops/ansible-mailman/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- Add the apex :envvar:`mailman__domain` to list of accepted referers. [drybjed_]


`debops.mailman v0.1.2`_ - 2016-07-09
-------------------------------------

.. _debops.mailman v0.1.2: https://github.com/debops/ansible-mailman/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Update the debops.unattended_upgrades_ configuration to latest changes.
  [drybjed_]


`debops.mailman v0.1.1`_ - 2016-03-30
-------------------------------------

.. _debops.mailman v0.1.1: https://github.com/debops/ansible-mailman/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Configure the site domain in Postfix using Ansible local facts.

  The site domain should be configured as ``mydestination`` when local mail is
  enabled in Postfix. It should not be set as a virtual domain in Mailman to
  not generate unnecessary virtual aliases, which break mail delivery.
  [drybjed_]

debops.mailman v0.1.0 - 2016-03-07
----------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Add configuration for debops.apt_preferences_ and
  debops.unattended_upgrades_ Ansible roles. [drybjed_]

- Add a default variable with custom debops.nginx_ server options for
  Mailman server. [drybjed_]

Changed
~~~~~~~

- Switch from patching the Mailman source code manually to using the ``patch``
  Ansible module. Patches are no longer copied to remote host and their state
  is not stored on the server, however it's easy to apply them again if
  necessary using a dedicated tag. [drybjed_]

- Perform UTF-8 conversion of Polish language pack only on Debian Wheezy and
  Ubuntu Precise, newer OS releases should be fine. [drybjed_]

- Restart Mailman on configuration changes. [drybjed_]

- Clean up APT package installation, expose list of packages in default
  variables. [drybjed_]

- Rewrite the language pack support.

  The role now exposes simple list of languages which is converted by a lookup
  template to set the ``debconf`` questions correctly. List of active languages
  is taken into account, so both data sources (Ansible default variables and
  ``debconf`` database) shouldn't fight over which languages are active
  anymore.

  The language pack conversion script has been rewritten to be idempotent and
  it's not installed on the remote host, but executed by the ``script`` module
  if any changes are detected. [drybjed_]

- Redesign the configuration of Mailman domains. The default domain is now set
  in a separate :envvar:`mailman__site_domain` variable, and additional virtual
  domains have their own list. [drybjed_]

- Clean up role tasks and handlers, conver them to YAML syntax. [drybjed_]

- Clean up Mailman configuration file. [drybjed_]

- Rename all variables to put them in a clear namespace. [drybjed_]

- Update documentation. [drybjed_]

- Reorder the fastcgi parameters in :program:`nginx` configuration to fix issue with
  `fcgiwrap interpreting the first occurrence <http://mailman.nginx.org/pipermail/nginx/2012-June/034224.html>`_
  of the variable instead of the last. [drybjed_]

Removed
~~~~~~~

- Remove hard role dependencies on debops.postfix_ and debops.nginx_.
  Configuration for debops.postfix_ and debops.nginx_ roles is defined in
  default variables, which can be passed to the roles through the playbook.

  Remove direct configuration of ``fcgiwrap`` instance and use
  debops.fcgiwrap_ role to configure a ``mailman`` instance. [drybjed_]

- Drop Ansible local facts related to Mailman. [drybjed_]
