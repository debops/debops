Changelog
=========

v0.1.0
------

*Unreleased*

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

