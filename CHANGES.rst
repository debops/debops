Changelog
=========

.. include:: includes/all.rst

**debops.postfix**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.postfix master`_ - unreleased
-------------------------------------

.. _debops.postfix master: https://github.com/debops/ansible-postfix/compare/v0.1.3...master


`debops.postfix v0.1.3`_ - 2017-07-11
-------------------------------------

.. _debops.postfix v0.1.3: https://github.com/debops/ansible-postfix/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Allow to use a global set of username and password in smtp_sasl_password_map
  instead of the per-host passwords. [drybjed_]

- Disable task that generates ``hash_aliases`` because they currently aren't
  used by the role and Ansible 2.2 stops role execution on missing templates.
  [drybjed_]

- Clean up documentation and Changelog. [drybjed_]


`debops.postfix v0.1.2`_ - 2016-03-30
-------------------------------------

.. _debops.postfix v0.1.2: https://github.com/debops/ansible-postfix/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add ``make`` package as a dependency. [pipitone]

Changed
~~~~~~~

- Allow ``!postscreen`` capability to disable ``postscreen`` filtering of
  incoming SMTP messages. [bleuchtang]

- Rename variables related to SASL authentication to be more generic instead of
  Cyrus-based. [bleuchtang]

- Fix "unexpected type error" when ``postfix`` variable has wrong value type.
  [htgoebel_]

- Fix deprecation warnings on Ansible 2.1.0. [thiagotalma_]

- Allow ``mydestination`` values to be set via Ansible local facts by other
  Ansible roles. [drybjed_]


`debops.postfix v0.1.1`_ - 2016-01-11
-------------------------------------

.. _debops.postfix v0.1.1: https://github.com/debops/ansible-postfix/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Use ``$LC_ALL`` variable instead of ``$LC_MESSAGES`` in a task to get the
  expected ``make`` output. [drybjed_]

Removed
~~~~~~~

- Remove redundant reload handlers and use only 1 handler to restart Postfix.
  [drybjed_]

- Remove not needed task that cleans up the firewall configuration. [drybjed_]


debops.postfix v0.1.0 - 2015-11-25
----------------------------------

Added
~~~~~

- First release. [drybjed_]

- Use ``$LC_MESSAGES`` to set correct locale instead of ``$LANG``. [drybjed_]

- Wrap IPv6 addresses in ``postfix_mynetworks`` in square brackets. [drybjed_]

- Expose the ``smtpd_banner`` variable in role default variables and hide the
  "Postfix" name in the banner. [drybjed_]

- debops.postfix_ incorrectly added a list value when requirement of
  a capability was not present. Now role will check if ``item.capability`` or
  ``item.no_capability`` are specified before adding a value or not. [drybjed_]

- debops.postfix_ incorrectly added a ``main.cf`` option with a value when
  a required capability was specified but was ``False``. Now role will check if
  an entry has specified value before deciding if it should be added. [drybjed_]

- Automatically enable or disable TLS certificates depending on status of the
  debops.pki_ role. [drybjed_]

- Use the Diffie-Hellman parameter files managed by debops.dhparam_ Ansible
  role. [drybjed_]

- Add ``postfix_capabilities`` variable which will define the list of Postfix
  capabilities. The old ``postfix`` variable is still present and will be
  removed at a later time. [drybjed_]

- Purge other SMTP server packages when Postfix is installed. [drybjed_]

- Replace the filewall configuration file with list of debops.ferm_
  configuration rules defined in default variables. [drybjed_]
