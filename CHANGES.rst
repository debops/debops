Changelog
=========

v0.3.1
------

*Unreleased*

- Add DebOps pre/post task hooks. [drybjed]

v0.3.0
------

*Released: 2015-03-30*

- Move all ``auth_ldap_*`` variables to ``auth_ldap_conf_`` namespace. [drybjed]

- ``auth_ldap`` variable is removed. Instead, ``/etc/ldap/ldap.conf`` is
  configured either if ``/etc/ldap/`` directory exists, or ``ldap`` is
  enabled in ``auth_nsswitch`` [drybjed]

- By a popular demand, ``auth_ldap_conf`` variable is brought back and can be
  used to disable configuration of ``/etc/ldap/ldap.conf``. [drybjed]

- ``auth_ldap_tls`` variable has been converted from a text block into separate
  TLS variables. [drybjed]

- Configuration of ``/etc/nsswitch.conf`` is slightly modified, now
  ``auth_nsswitch`` variable controls presence and order of specific database
  entries in the configuration file. [drybjed]

- Add LDAP filtering in ``/etc/nslcd.conf``. By default ``nslcd`` will only
  search LDAP accounts with ``uid`` greater than 1000. With additional
  ``ldapns`` schema enabled in OpenLDAP server, only accounts with specific
  attributes will be allowed to login. [drybjed]

v0.2.1
------

*Released: 2015-02-25*

- ``debops.auth`` LDAP configuration tasks will now use new LDAP support in
  ``debops.secret``. [drybjed]

- Required Ansible version is changed to ``1.8.0+``. [drybjed]

- ``nslcd`` daemon will now be correctly restarted when its configuration file
  is changed. [drybjed]

- You can now specify the scrutiny level which ``nslcd`` will use while
  verifying the certificate sent by the LDAP server. [drybjed]

v0.2.0
------

*Released: 2015-02-24*

- Add NSS LDAP / PAM authentication support [drybjed]

v0.1.0
------

*Released: 2015-02-20*

- First release [drybjed]

