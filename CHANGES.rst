Changelog
=========

v0.2.2
------

*Released: 2015-08-27*

- Use correct name of the ``debops.postfix`` dependent parameter. [drybjed]


v0.2.1
------

*Released: 2015-08-19*

- Add support for LMTP mail delivery protocol. If enabled it will depend
  on ``debops.postfix`` by default and configure it to use Dovecot LMTP
  for mail delivery. [ganto]


v0.2.0
------

*Released: 2015-08-16*

- Add ``dovecot_<protocol>_listeners`` to manage multiple listeners per
  protocol (e.g. IMAP/IMAPS). Ability to customize and add additional network
  listeners. ``imaps/pop3s`` shouldn't be used in ``dovecot_protocols``
  anymore now. [ganto]

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

