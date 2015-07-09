Changelog
=========

v0.1.0
------

*Unreleased*

- First release, add CHANGES.rst [drybjed]

- Change the default ``olcAccess`` rules to not allow users to modify all of
  their own attributes by default. Fixes `Debian Bug #761406`_. [drybjed]

.. _Debian Bug #761406: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=761406

- Move ``olcSecurity`` rules to role defaults, so that they can be easily
  overridden if necessary. [drybjed]

- Add a variable that specifies LDAP database backend that's in use. On Debian
  Wheezy it's set to ``hdb`` by default, on Debian Jessie and other
  distributions it's set to ``mdb`` by default. [drybjed]

- Add ``openssh-lpk`` LDAP schema for support of OpenSSH Public Key lookup in
  LDAP server. [drybjed]

