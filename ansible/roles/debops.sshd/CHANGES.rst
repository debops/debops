Changelog
=========

.. include:: includes/all.rst

**debops.sshd**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.sshd master`_ - unreleased
----------------------------------

.. _debops.sshd master: https://github.com/debops/ansible-sshd/compare/v0.3.0...master


`debops.sshd v0.3.0`_ - 2017-07-12
----------------------------------

.. _debops.sshd v0.3.0: https://github.com/debops/ansible-sshd/compare/v0.2.5...v0.3.0

Added
~~~~~

- When OpenSSH server is installed for the first time, make sure that the
  service is not started before being properly secured. [sourcejedi]

Changed
~~~~~~~

- LDAP lookup script now works with binary and text attributes. [pedroluislopez_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Update the :file:`sshd.fact` script to fix communication problems with an
  external :command:`dpkg-query` command. [bfabio_]

- Update the parameters of the debops.ferm_ configuration to use new features
  introduced in the role. This might affect the firewall rules of the SSH
  service, therefore check first if your configuration is applied properly.
  Ansible inventory modification shouldn't be necessary. [drybjed_]

- Don't include deprecated configuration options in the
  :file:`/etc/ssh/sshd_config` configuration file. [drybjed_]

- Increase the default ``LoginGraceTime`` value from 20 to 30 seconds to help
  solve issues with unresponsive DNS servers. [drybjed_]

Deprecated
~~~~~~~~~~

- The ``openssh-blacklist*`` Debian packages have been removed from Debian
  Archive and won't be available in Debian Stretch onwards.
  Ref: https://bugs.debian.org/859682 [ypid_, drybjed_]


`debops.sshd v0.2.5`_ - 2016-10-10
----------------------------------

.. _debops.sshd v0.2.5: https://github.com/debops/ansible-sshd/compare/v0.2.4...v0.2.5

Changed
~~~~~~~

- Moved some packages from :envvar:`sshd__base_packages` to
  :envvar:`sshd__recommended_packages` and :envvar:`sshd__optional_packages` to
  allow to overwrite them. [ypid_]

- Use the ``accept_any`` parameter in debops.tcpwrappers_ role configuration
  to enable or disable entries depending on which lists of allowed hosts are
  active. [drybjed_]


`debops.sshd v0.2.4`_ - 2016-07-31
----------------------------------

.. _debops.sshd v0.2.4: https://github.com/debops/ansible-sshd/compare/v0.2.3...v0.2.4

Added
~~~~~

- Added :envvar:`sshd__ciphers_additional`,
  :envvar:`sshd__kex_algorithms_additional` and :envvar:`sshd__macs_additional`
  to allow to specify additional cryptography related settings which are also
  applied in :envvar:`sshd__paranoid` mode.
  This is needed for the ``debops-contrib.x2go_server`` role.
  [ypid_]

- Replace static Ansible fact file with a script that exposes some ``sshd``
  configuration variables as Ansible facts. [ganto_]

Changed
~~~~~~~

- Fixed Ansible check mode support to not fail when running with
  ``ansible_connection=local`` against a host which does not have ``sshd``
  installed yet. [ypid_]

- Make sure that not registered conditional variable returns an empty list.
  [cultcom]

- Update documentation and Changelog. [drybjed_]


`debops.sshd v0.2.3`_ - 2016-02-21
----------------------------------

.. _debops.sshd v0.2.3: https://github.com/debops/ansible-sshd/compare/v0.2.2...v0.2.3

Added
~~~~~

- Automatically remove Diffie-Hellman parameters from :file:`/etc/ssh/moduli` which
  are smaller than the size specified in ``sshd_moduli_minimum`` variable (by
  default 2048 bits). [drybjed_]

Changed
~~~~~~~

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]

- Rename all role variables to put them in ``sshd__`` namespace. You might need
  to update your Ansible inventory. [drybjed_]


`debops.sshd v0.2.2`_ - 2015-11-13
----------------------------------

.. _debops.sshd v0.2.2: https://github.com/debops/ansible-sshd/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Make sure that role works in Ansible check mode. [drybjed_]

Removed
~~~~~~~

- Removed ``debops.sshkeys`` from role dependencies as it is also run from the
  :file:`common.yml` playbook. [ypid_]

- Remove most of the Ansible role dependencies, leaving only those that are
  required for the role to run correctly.

  Configuration of dependent services like firewall, TCP Wrappers, APT
  preferences is set in separate default variables. These variables can be used
  by Ansible playbooks to configure settings related to ``sshd`` in other
  services. [drybjed_]


`debops.sshd v0.2.1`_ - 2015-08-16
----------------------------------

.. _debops.sshd v0.2.1: https://github.com/debops/ansible-sshd/compare/v0.2.0...v0.2.1

Added
~~~~~

- New variable ``sshd_paranoid``, allows to limit the use of various encryption
  algorithms to only first (presumed safest) choice. [ypid_]

Changed
~~~~~~~

- ``sshd_custom_options`` variable has been moved to top of the ``sshd_config``
  file, that way it can be used to override any option if necessary, since
  ``sshd`` uses first instance of an option it finds in the config file. [ypid_]


`debops.sshd v0.2.0`_ - 2015-08-16
----------------------------------

.. _debops.sshd v0.2.0: https://github.com/debops/ansible-sshd/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add debops.secret_ role dependency, it's needed for access to LDAP
  secrets. [drybjed_]

- Add debops.apt_preferences_ role dependency. OpenSSH from
  ``wheezy-backports`` will be installed on Debian Wheezy, if the repository is
  present. This brings version parity with Debian Jessie (current Stable), adds
  support for better encryption ciphers and allows to look up SSH public keys
  in external authentication sources. [drybjed_]

- Add separate ``sshd_ferm_ports`` variable which is a list that defines what
  ports are opened in the firewall for access to OpenSSH server. By default
  only :command:`ssh` port from :file:`/etc/services` is opened. [drybjed_]

- Add tags for debops.tcpwrappers_ and ``debops.sshkeys`` role dependencies.
  [drybjed_]

- Add ``sshd_listen`` list which can be used to specify IP addresses of
  interfaces on which ``sshd`` should listen for new connections. If list is
  not specified, ``sshd`` will listen on all interfaces. [drybjed_]

- Add configuration variables for ``MaxAuthTries`` and ``LoginGraceTime``
  options. [drybjed_]

- Create ``Ed25519`` host key if it's not present and OpenSSH version supports
  it. [drybjed_]

- Add support for public key lookup in external sources.

  Support for ``AuthorizedKeysCommand`` option will be disabled by default, and
  can be enabled on Debian Jessie as well as on Debian Wheezy with backported
  OpenSSH version using ``sshd_authorized_keys_lookup`` variable. Scripts that
  perform the lookups will be executed on a separate system UNIX account to
  provide privilege separation. [drybjed_]

- Add LDAP lookup script and configuration.

  When a host is configured using debops.auth_ to access account information
  from LDAP and system-wide configuration in :file:`/etc/ldap/ldap.conf` is set
  properly, OpenSSH can perform LDAP lookups using external script to retrieve
  valid SSH public keys. LDAP lookup will be configured by default if
  ``AuthorizedKeysCommand`` lookup is enabled on a host. [drybjed_]

- Add missing tags to Ansible tasks. [drybjed_]

Changed
~~~~~~~

- Request :command:`sudo` access on Travis-CI. [drybjed_]

- Update documentation. [drybjed_]

- Change how OpenSSH packages are managed.

  Main list of packages is moved to ``sshd_base_packages`` variable,
  ``sshd_packages`` is an empty list which can be used to include additional
  packages if needed.

  By default ``debops.sshd`` will automatically upgrade packages - this is
  needed on Debian Wheezy to install newer version of OpenSSH from
  ``wheezy-backports``. To disable automatic upgrades, role will add a separate
  local fact which indicates that ``debops.sshd`` is configured on a given
  host. This will automatically switch the :command:`apt` module from upgrading the
  packages to ensuring that they are present. [drybjed_]

- Rename ``sshd_config_ports`` to ``sshd_ports``. [drybjed_]

- Rename ``sshd_PermitRootLogin`` to ``sshd_permit_root_login``. [drybjed_]

- Rename ``sshd_PasswordAuthentication`` to ``sshd_password_authentication``.
  [drybjed_]

- Rename ``sshd_X11Forwarding`` to ``sshd_x11_forwarding``. [drybjed_]

- Rename ``sshd_AllowGroups`` to ``sshd_allow_groups`` and expand it to
  additional lists, ``sshd_group_allow_groups`` and ``sshd_host_allow_groups``.

  Variable is converted from a string to a YAML list. List of system groups
  that are allowed to login hasn't been changed. If no groups are specified,
  option is not enabled and no limits are imposed by ``sshd``. [drybjed_]

- Reorganize various ``sshd_authorized_keys*`` variables into a list split into
  "system" and "user" authorized key files. Support for Monkeysphere authorized
  keys out of the box is dropped, might be re-added in the future if there is
  interest. [drybjed_]

- Make ``PrivilegeSeparation`` option configurable. [drybjed_]

- Make ``LogLevel`` configurable. [drybjed_]

- Make ``MaxStartups`` option configurable. [drybjed_]

- Make ``Banner`` option configurable. [drybjed_]

- Refactor ``Ciphers``, ``KexAlgorithms`` and ``MACs`` options.

  Various OpenSSH encryption options are not static anymore. Instead,
  ``debops.sshd`` will check what version of OpenSSH package is installed on
  a host and will pick a list of algorithms for each of the mentioned options
  from a defined set according to what version is installed, to make sure that
  there won't be an issue with unsupported ciphers.

  Current set of algorithms has been taken from Mozilla and should work with
  OpenSSH available in Debian Jessie. There's a separate set of algorithms for
  Debian Wheezy without backported OpenSSH installed as well. [drybjed_]

- Make ``Match`` options configurable.

  Static ``Match`` options defined previously are moved to
  a ``sshd_match_list`` list variable, with a SFTPonly configuration enabled by
  default.

  SFTPonly configuration will now use global ``PasswordAuthentication`` option
  instead of forcibly disabling password authentication. [drybjed_]

- Update :file:`defaults/main.yml` file to support ``.rst`` documentation and add
  whitespace in various files for better readability. [drybjed_]

Removed
~~~~~~~

- Remove :file:`tasks/backup.yml` and :file:`tasks/restore.yml`, they are not used in
  main role task list. [drybjed_]

- Remove debops.auth_ role dependency. Configuration done by this role is
  assumed to be present, since it's executed as part of the :file:`common.yml`
  playbook. [drybjed_]

- Remove ``sshd_HostKey`` list. Instead of a static list of host keys,
  ``debops.sshd`` role will check what host keys are present in :file:`/etc/ssh/`
  directory. Using ``sshd_host_keys`` list which provides types of keys and
  their preferred order, host keys that are present will be added to ``sshd``
  configuration file. [drybjed_]

- Remove ``sshd_config_options_begin`` and ``sshd_config_options_end``
  variables and replace them with with ``sshd_custom_options`` YAML text block
  variable. [drybjed_]


debops.sshd v0.1.0 - 2015-08-10
-------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]
