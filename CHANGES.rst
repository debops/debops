Changelog
=========

v0.1.0
------

*Unreleased*

- Expose the ``smtpd_banner`` variable in role default variables and hide the
  "Postfix" name in the banner. [drybjed]

- Wrap IPv6 addresses in ``postfix_mynetworks`` in square brackets. [drybjed]

- Use ``$LC_MESSAGES`` to set correct locale instead of ``$LANG``. [drybjed]

- First release [drybjed]

