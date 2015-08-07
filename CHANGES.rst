Changelog
=========

v0.2.0
------

*Unreleased*

- Introduce new protocol-specific configuration dictionary
  ``dovecot_<protocol>_config_map`` which allows to customize every variable
  related to the ``service`` and ``protocol`` sections of the protocols.
  So far, this works for the IMAP, POP3, Managesieve and LDA protocols.
  The ``dovecot_allow_<protocol>`` variables were removed. The network
  peers can now also be restricted via the new configuration dictionary
  mentioned above. [ganto]


v0.1.0
------

*Released: 2015-04-01*

- First release [ganto, drybjed]

