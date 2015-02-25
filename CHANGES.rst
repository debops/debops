Changelog
=========

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

