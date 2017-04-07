Changelog
=========

**debops.auth**

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.auth master`_ - unreleased
----------------------------------

.. _debops.auth master: https://github.com/debops/ansible-auth/compare/v0.3.5...master


`debops.auth v0.3.5`_ - 2017-04-07
----------------------------------

.. _debops.auth v0.3.5: https://github.com/debops/ansible-auth/compare/v0.3.4...v0.3.5

Removed
~~~~~~~

- Remove management of the :file:`/etc/nsswitch.conf` configuration file. This
  functionality has been moved to the new ``debops.nsswitch`` Ansible role.
  [drybjed_]


`debops.auth v0.3.4`_ - 2017-01-13
----------------------------------

.. _debops.auth v0.3.4: https://github.com/debops/ansible-auth/compare/v0.3.3...v0.3.4

Fixed
~~~~~

- Fix wrong condition syntax in admin users task. [drybjed_]


`debops.auth v0.3.3`_ - 2017-01-11
----------------------------------

.. _debops.auth v0.3.3: https://github.com/debops/ansible-auth/compare/v0.3.2...v0.3.3

Added
~~~~~

- Make sure that the system administrator accounts are present and included in
  the specific admin groups. [drybjed]

Removed
~~~~~~~

- Remove ``auth_shadow_umask`` variable. It set the umask for a lot more cases than
  just the home directories. You can now set the umask for home directories with the
  ``debops.users`` role. [bfabio]


`debops.auth v0.3.2`_ - 2016-11-17
----------------------------------

.. _debops.auth v0.3.2: https://github.com/debops/ansible-auth/compare/v0.3.1...v0.3.2

Added
~~~~~

- Add ``!requiretty`` to :command:`sudo` default variables. [jstruebel]

- Add a way to enable or disable :command:`nslcd` support via a boolean
  variable. [le9i0nx]

Changed
~~~~~~~

- Use ``{{ ansible_managed }}`` variable in templates. [jstruebel]

- Update the task that uses ``ldap_entry`` module to the latest changes in the
  module parameter syntax. [drybjed]


`debops.auth v0.3.1`_ - 2016-07-08
----------------------------------

.. _debops.auth v0.3.1: https://github.com/debops/ansible-auth/compare/v0.3.0...v0.3.1

Added
~~~~~

- Add DebOps pre/post task hooks. [drybjed]

- Add variable to specify umask for new home directories created by
  ``pam_mkhomedir`` PAM module. Default umask is set to ``0027``. [drybjed]

- Set the default ``UMASK`` value for ``useradd`` command to ``0027``. All new
  home directories will have ``0750`` permissions, which might affect content
  accessibility for different applications. [drybjed]

- Add support for ``pam_cracklib`` to enforce harder UNIX passwords. [drybjed]

- Remember previous 5 passwords set on each account using ``pam_pwhistory``
  module to enforce use of different passwords. [drybjed]

- Role will check if ``libnss-mdns`` package is present and enable/disable
  mDNS/Avahi support in ``/etc/nsswitch.conf`` accordingly. [drybjed]

- Add the ``COPYRIGHT`` file. [drybjed]

Changed
~~~~~~~

- Change location of machine password in ``secret/``.

  Change where LDAP machine bind password is stored in ``secret/`` directory to
  make it more general and not based on ``nslcd``. This should make sharing
  machine password between different services easier.

  If administrator does not move passwords to new location in ``secret/``
  directory, this will result in Ansible creating new random passwords for each
  host and updating them in LDAP. This may require update of the machine
  password for each service that uses it. [drybjed]

- Change default machine password length to 48 characters. [drybjed]

- Allow for per-domain access in LDAP host filter. [drybjed]

- Change quotes in ``lineinfile`` task to correctly pass Tab characters through
  the template engine. [drybjed]

- Update Changelog to latest DebOps role standards. [drybjed]

- Switch ``sudo`` task parameter to ``become``. [drybjed]

Removed
~~~~~~~

- Remove ``auth_admin_accounts`` list and related tasks. This list was used to
  create admin accounts, which interfered when these accounts were supposed to
  be system accounts instead of normal "user" accounts.

  Use the ``debops.users`` role instead to create local administrator accounts
  and add them to the ``admins`` group to grant them admin access.
  Bootstrap playbooks / scripts should do that automatically for default admin
  account. [drybjed]

- Cease management of ``su`` PAM configuration. Only thing that was managed was
  passwordless access given to specific system group; ``sudo`` is sufficient
  for this functionality. Already existing systems are unchanged. [drybjed]

Fixed
~~~~~

- Fix support for Ansible ``--check`` mode. [drybjed]

- Fix Ansible deprecation warning about undefined variable. [drybjed]


`debops.auth v0.3.0`_ - 2015-03-30
----------------------------------

.. _debops.auth v0.3.0: https://github.com/debops/ansible-auth/compare/v0.2.1...v0.3.0

Added
~~~~~

- By a popular demand, ``auth_ldap_conf`` variable is brought back and can be
  used to disable configuration of ``/etc/ldap/ldap.conf``. [drybjed]

- Add LDAP filtering in ``/etc/nslcd.conf``. By default ``nslcd`` will only
  search LDAP accounts with ``uid`` greater than 1000. With additional
  ``ldapns`` schema enabled in OpenLDAP server, only accounts with specific
  attributes will be allowed to login. [drybjed]

Changed
~~~~~~~

- Move all ``auth_ldap_*`` variables to ``auth_ldap_conf_`` namespace. [drybjed]

- ``auth_ldap_tls`` variable has been converted from a text block into separate
  TLS variables. [drybjed]

- Configuration of ``/etc/nsswitch.conf`` is slightly modified, now
  ``auth_nsswitch`` variable controls presence and order of specific database
  entries in the configuration file. [drybjed]

Removed
~~~~~~~

- ``auth_ldap`` variable is removed. Instead, ``/etc/ldap/ldap.conf`` is
  configured either if ``/etc/ldap/`` directory exists, or ``ldap`` is
  enabled in ``auth_nsswitch`` [drybjed]


`debops.auth v0.2.1`_ - 2015-02-25
----------------------------------

.. _debops.auth v0.2.1: https://github.com/debops/ansible-auth/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- ``debops.auth`` LDAP configuration tasks will now use new LDAP support in
  ``debops.secret``. [drybjed]

- Required Ansible version is changed to ``1.8.0+``. [drybjed]

- ``nslcd`` daemon will now be correctly restarted when its configuration file
  is changed. [drybjed]

- You can now specify the scrutiny level which ``nslcd`` will use while
  verifying the certificate sent by the LDAP server. [drybjed]


`debops.auth v0.2.0`_ - 2015-02-24
----------------------------------

.. _debops.auth v0.2.0: https://github.com/debops/ansible-auth/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add NSS LDAP / PAM authentication support. [drybjed]


debops.auth v0.1.0 - 2015-02-20
-------------------------------

Added
~~~~~

- First release. [drybjed]

