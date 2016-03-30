Changelog
=========

v0.1.2
------

*Released: 2016-03-30*

- Add ``make`` package as a dependency. [pipitone]

- Allow ``!postscreen`` capability to disable ``postscreen`` filtering of
  incoming SMTP messages. [bleuchtang]

- Rename variables related to SASL authentication to be more generic instead of
  Cyrus-based. [bleuchtang]

- Fix "unexpected type error" when ``postfix`` variable has wrong value type.
  [htgoebel]

- Fix deprecation warnings on Ansible 2.1.0. [thiagotalma]

- Allow ``mydestination`` values to be set via Ansible local facts by other
  Ansible roles. [drybjed]

v0.1.1
------

*Released: 2016-01-11*

- Remove redundant reload handlers and use only 1 handler to restart Postfix.
  [drybjed]

- Remove not needed task that cleans up the firewall configuration. [drybjed]

- Use ``$LC_ALL`` variable instead of ``$LC_MESSAGES`` in a task to get the
  expected ``make`` output. [drybjed]

v0.1.0
------

*Released: 2015-11-25*

- First release [drybjed]

- Use ``$LC_MESSAGES`` to set correct locale instead of ``$LANG``. [drybjed]

- Wrap IPv6 addresses in ``postfix_mynetworks`` in square brackets. [drybjed]

- Expose the ``smtpd_banner`` variable in role default variables and hide the
  "Postfix" name in the banner. [drybjed]

- ``debops.postfix`` incorrectly added a list value when requirement of
  a capability was not present. Now role will check if ``item.capability`` or
  ``item.no_capability`` are specified before adding a value or not. [drybjed]

- ``debops.postfix`` incorrectly added a ``main.cf`` option with a value when
  a required capability was specified but was ``False``. Now role will check if
  an entry has specified value before deciding if it should be added. [drybjed]

- Automatically enable or disable TLS certificates depending on status of the
  ``debops.pki`` role. [drybjed]

- Use the Diffie-Hellman parameter files managed by ``debops.dhparam`` Ansible
  role. [drybjed]

- Add ``postfix_capabilities`` variable which will define the list of Postfix
  capabilities. The old ``postfix`` variable is still present and will be
  removed at a later time. [drybjed]

- Purge other SMTP server packages when Postfix is installed. [drybjed]

- Replace the filewall configuration file with list of ``debops.ferm``
  configuration rules defined in default variables. [drybjed]

