Changelog
=========

v0.2.3
------

*Released: 2016-02-21*

- Fix deprecation warnings on Ansible 2.1.0. [drybjed]

- Automatically remove Diffie-Hellman parameters from ``/etc/ssh/moduli`` which
  are smaller than the size specified in ``sshd_moduli_minimum`` variable (by
  default 2048 bits). [drybjed]

- Rename all role variables to put them in ``sshd__`` namespace. You might need
  to update your Ansible inventory. [drybjed]

v0.2.2
------

*Released: 2015-11-13*

- Removed ``debops.sshkeys`` from role dependencies as it is also run from the
  ``common.yml`` playbook. [ypid]

- Remove most of the Ansible role dependencies, leaving only those that are
  required for the role to run correctly.

  Configuration of dependent services like firewall, TCP Wrappers, APT
  preferences is set in separate default variables. These variables can be used
  by Ansible playbooks to configure settings related to ``sshd`` in other
  services. [drybjed]

- Make sure that role works in Ansible check mode. [drybjed]

v0.2.1
------

*Released: 2015-08-16*

- ``sshd_custom_options`` variable has been moved to top of the ``sshd_config``
  file, that way it can be used to override any option if necessary, since
  ``sshd`` uses first instance of an option it finds in the config file. [ypid]

- New variable ``sshd_paranoid``, allows to limit the use of various encryption
  algorithms to only first (presumed safest) choice. [ypid]

v0.2.0
------

*Released: 2015-08-16*

- Remove ``tasks/backup.yml`` and ``tasks/restore.yml``, they are not used in
  main role task list. [drybjed]

- Request ``sudo`` access on Travis-CI. [drybjed]

- Update documentation. [drybjed]

- Remove ``debops.auth`` role dependency. Configuration done by this role is
  assumed to be present, since it's executed as part of the ``common.yml``
  playbook. [drybjed]

- Add ``debops.secret`` role dependency, it's needed for access to LDAP
  secrets. [drybjed]

- Add ``debops.apt_preferences`` role dependency. OpenSSH from
  ``wheezy-backports`` will be installed on Debian Wheezy, if the repository is
  present. This brings version parity with Debian Jessie (current Stable), adds
  support for better encryption ciphers and allows to look up SSH public keys
  in external authentication sources. [drybjed]

- Add separate ``sshd_ferm_ports`` variable which is a list that defines what
  ports are opened in the firewall for access to OpenSSH server. By default
  only ``ssh`` port from ``/etc/services`` is opened. [drybjed]

- Add tags for ``debops.tcpwrappers`` and ``debops.sshkeys`` role dependencies.
  [drybjed]

- Change how OpenSSH packages are managed.

  Main list of packages is moved to ``sshd_base_packages`` variable,
  ``sshd_packages`` is an empty list which can be used to include additional
  packages if needed.

  By default ``debops.sshd`` will automatically upgrade packages - this is
  needed on Debian Wheezy to install newer version of OpenSSH from
  ``wheezy-backports``. To disable automatic upgrades, role will add a separate
  local fact which indicates that ``debops.sshd`` is configured on a given
  host. This will automatically switch the ``apt`` module from upgrading the
  packages to ensuring that they are present. [drybjed]

- Rename ``sshd_config_ports`` to ``sshd_ports``. [drybjed]

- Rename ``sshd_PermitRootLogin`` to ``sshd_permit_root_login``. [drybjed]

- Rename ``sshd_PasswordAuthentication`` to ``sshd_password_authentication``.
  [drybjed]

- Rename ``sshd_X11Forwarding`` to ``sshd_x11_forwarding``. [drybjed]

- Rename ``sshd_AllowGroups`` to ``sshd_allow_groups`` and expand it to
  additional lists, ``sshd_group_allow_groups`` and ``sshd_host_allow_groups``.

  Variable is converted from a string to a YAML list. List of system groups
  that are allowed to login hasn't been changed. If no groups are specified,
  option is not enabled and no limits are imposed by ``sshd``. [drybjed]

- Reorganize various ``sshd_authorized_keys*`` variables into a list split into
  "system" and "user" authorized key files. Support for Monkeysphere authorized
  keys out of the box is dropped, might be re-added in the future if there is
  interest. [drybjed]

- Add ``sshd_listen`` list which can be used to specify IP addresses of
  interfaces on which ``sshd`` should listen for new connections. If list is
  not specified, ``sshd`` will listen on all interfaces. [drybjed]

- Remove ``sshd_HostKey`` list. Instead of a static list of host keys,
  ``debops.sshd`` role will check what host keys are present in ``/etc/ssh/``
  directory. Using ``sshd_host_keys`` list which provides types of keys and
  their preferred order, host keys that are present will be added to ``sshd``
  configuration file. [drybjed]

- Make ``PrivilegeSeparation`` option configurable. [drybjed]

- Make ``LogLevel`` configurable. [drybjed]

- Make ``MaxStartups`` option configurable. [drybjed]

- Add configuration variables for ``MaxAuthTries`` and ``LoginGraceTime``
  options. [drybjed]

- Make ``Banner`` option configurable. [drybjed]

- Refactor ``Ciphers``, ``KexAlgorithms`` and ``MACs`` options.

  Various OpenSSH encryption options are not static anymore. Instead,
  ``debops.sshd`` will check what version of OpenSSH package is installed on
  a host and will pick a list of algorithms for each of the mentioned options
  from a defined set according to what version is installed, to make sure that
  there won't be an issue with unsupported ciphers.

  Current set of algorithms has been taken from Mozilla and should work with
  OpenSSH available in Debian Jessie. There's a separate set of algorithms for
  Debian Wheezy without backported OpenSSH installed as well. [drybjed]

- Remove ``sshd_config_options_begin`` and ``sshd_config_options_end``
  variables and replace them with with ``sshd_custom_options`` YAML text block
  variable. [drybjed]

- Make ``Match`` options configurable.

  Static ``Match`` options defined previously are moved to
  a ``sshd_match_list`` list variable, with a SFTPonly configuration enabled by
  default.

  SFTPonly configuration will now use global ``PasswordAuthentication`` option
  instead of forcibly disabling password authentication. [drybjed]

- Create ``Ed25519`` host key if it's not present and OpenSSH version supports
  it. [drybjed]

- Add support for public key lookup in external sources.

  Support for ``AuthorizedKeysCommand`` option will be disabled by default, and
  can be enabled on Debian Jessie as well as on Debian Wheezy with backported
  OpenSSH version using ``sshd_authorized_keys_lookup`` variable. Scripts that
  perform the lookups will be executed on a separate system UNIX account to
  provide privilege separation. [drybjed]

- Add LDAP lookup script and configuration.

  When a host is configured using ``debops.auth`` to access account information
  from LDAP and system-wide configuration in ``/etc/ldap/ldap.conf`` is set
  properly, OpenSSH can perform LDAP lookups using external script to retrieve
  valid SSH public keys. LDAP lookup will be configured by default if
  ``AuthorizedKeysCommand`` lookup is enabled on a host. [drybjed]

- Add missing tags to Ansible tasks. [drybjed]

- Update ``defaults/main.yml`` file to support ``.rst`` documentation and add
  whitespace in various files for better readability. [drybjed]

v0.1.0
------

*Released: 2015-08-10*

- Add Changelog. [drybjed]

