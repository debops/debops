.. _changelog:

Changelog
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <https://keepachangelog.com/en/1.0.0/>`__.

This file contains only general overview of the changes in the DebOps project.
The detailed changelog can be seen using :command:`git log` command.

You can read information about required changes between releases in the
:ref:`upgrade_notes` documentation.


`debops stable-1.0`_ - unreleased
---------------------------------

.. _debops stable-1.0: https://github.com/debops/debops/compare/v1.0.0...stable-1.0


`debops v1.0.5`_ - 2019-07-12
-----------------------------

.. _debops v1.0.5: https://github.com/debops/debops/compare/v1.0.4...v1.0.5

Changed
~~~~~~~

- [debops.netbase] Do not try to manage the hostname in LXC, Docker or OpenVZ
  containers by default. We assume that these containers are unprivileged and
  their hostname cannot be changed from the inside of the container.

- [debops.sudo] Configure the :command:`sudo` LDAP support before installing
  the ``sudo-ldap`` APT package to ensure that access to the ``root`` account
  is available.

- [debops.dovecot] Expose the configuration of the Sieve directory and
  configuration file via role default variables.

- [debops.apt] The Debian and Raspbian suites have been updated to reflect the
  release of Debian Buuster. Congratulations!

- [debops.nslcd] Remove comments from the PAM configuration file to stop the
  :command:`pam-auth-update` script from complaining about them.

Fixed
~~~~~

- [debops.ldap] Avoid gathering MAC addresses from network interfaces that do
  not have them, for example interfaces with multiple IPv4 addresses.

- [debops.sudo] Allow the :command:`dpkg` command to remove the ``sudo`` APT
  package even if the ``root`` password is not set (required for installing the
  ``sudo-ldap`` APT package).

- [debops.elasticsearch] Divert the sysctl configuration file that comes with
  the Elasticsearch .deb package to fix use of the :command:`sysctl --system`
  command inside containers. The configuration will be applied by the
  :ref:`debops.sysctl` role instead.

- [debops.redis_server] Fix deployment of Redis Server without a password set.


`debops v1.0.4`_ - 2019-06-25
-----------------------------

.. _debops v1.0.4: https://github.com/debops/debops/compare/v1.0.3...v1.0.4

Added
~~~~~

- [LDAP] The :file:`ldap/init-directory.yml` Ansible playbook will create an
  LDAP group object for SSH users, equivalent to the ``sshusers`` group created
  by the :ref:`debops.system_groups` role. LDAP accounts in this group will be
  able to access SSH service from any host. Existing installations might need
  to be updated manually to fix UID/GID or LDAP DN conflicts.

Fixed
~~~~~

- [debops.dnsmasq] Fix configuration of external boot servers in the
  :command:`dnsmasq` service, and work around the issue with ``ipaddr`` filter
  in Ansible 2.8 in the :ref:`debops.dnsmasq` role.

- [debops.core] Fix Python 3.x compatibility in the :file:`core.fact` script.

- The role dependencies defined in the :file:`meta/main.yml` files in roles
  published in the Ansible Galaxy Collection will have their ``debops.`` prefix
  removed to make the roles usable.


`debops v1.0.3`_ - 2019-06-21
-----------------------------

.. _debops v1.0.3: https://github.com/debops/debops/compare/v1.0.2...v1.0.3

Fixed
~~~~~

- [debops.apt_install] The role will not disable :command:`needrestart` kernel
  hints if the ``needrestart`` APT package installation is disabled. This fixes
  an issue with the :file:`/etc/needrestart/conf.d/` directory not being
  present on the host.

- [debops.gitlab_runner] Fix typo in the configuration template.

- [debops.postgresql_server] Fix usage of the Ansible ``--check`` mode with the
  ``role::postgresql_server:config`` tag to allow checking configuration
  changes before applying them.

- [debops.lxc] Implement a workaround for the issue of the ``ipaddr`` Ansible
  filter incorrectly interpreting index numbers specified as strings in Ansible
  v2.8.x, used in the :file:`/etc/default/lxc-net.j2` template.


`debops v1.0.2`_ - 2019-05-31
-----------------------------

.. _debops v1.0.2: https://github.com/debops/debops/compare/v1.0.1...v1.0.2

Fixed
~~~~~

- [debops.nginx] Allow empty ``item.name`` parameter which tells the role to
  not include a ``server_name`` option in a :command:`nginx` server
  configuration.

- [debops.root_account][debops.system_users][debops.users] Fix idempotency
  issue with :command:`yadm` updating repositories on newer OS releases with
  changed :command:`git` output. The roles will also work without
  :command:`yadm` installed when user accounts have dotfiles enabled
  explicitly.


`debops v1.0.1`_ - 2019-05-23
-----------------------------

.. _debops v1.0.1: https://github.com/debops/debops/compare/v1.0.0...v1.0.1

Changed
~~~~~~~

- [debops.system_users] Use a custom script to get current Ansible user
  information because the ``getent`` Ansible module does not work on Apple
  macOS.


`debops v1.0.0`_ - 2019-05-22
-----------------------------

.. _debops v1.0.0: https://github.com/debops/debops/compare/v0.8.1...v1.0.0

Added
~~~~~

- New DebOps roles:

  - :ref:`debops.docker_registry` role provides support for Docker Registry.
    The role can be used as standalone or as a backend for the GitLab Container
    Registry service, with :ref:`debops.gitlab` role.

  - :ref:`debops.ldap` role sets up the system-wide LDAP configuration on
    a host, and is used as the API to the LDAP directory by other Ansible
    roles, playbooks, and users via Ansible inventory. The role is included in
    the ``common.yml`` playbook, but is disabled by default.

  - :ref:`debops.nslcd` role can be used to configure LDAP lookups for NSS and
    PAM services on a Linux host.

  - :ref:`debops.pam_access` role manages PAM access control files located in
    the :file:`/etc/security/` directory. The role is designed to allow other
    Ansible roles to easily manage their own PAM access rules.

  - :ref:`debops.yadm` role installs the `Yet Another Dotfiles Manager`__
    script and ensures that additional shells are available. It can also mirror
    dotfiles locally. The role is included in the common playbook.

    .. __: https://yadm.io/

  - :ref:`debops.system_users` role replaces the ``debops.bootstrap`` role and
    is used to manage the local system administrator accounts. It is included
    in the :file:`common.yml` playbook as well as the bootstrap playbooks.

- [debops.nginx] The role will automatically generate configuration which
  redirects short hostnames or subdomains to their FQDN equivalents. This
  allows HTTP clients to reach websites by specifying their short names via DNS
  suffixes from :file:`/etc/resolv.conf` file, or using ``*.local`` domain
  names managed by Avahi/mDNS to redirect HTTP clients to the correct FQDNs.

- [debops.resources] Some lists can now configure ACL entries on the destination
  files or directories using the ``item.acl`` parameter. Take a look to
  :ref:`resources__ref_acl` section to have the list of compatibles variables.

- [debops.lxc] Users can now disable default route advertisement in the
  ``lxc-net`` DHCP service. This is useful in cases where LXC containers have
  multiple network interfaces and the default route should go through
  a different gateway than the LXC host.

- [debops.lxc] The :command:`lxc-new-unprivileged` script will add missing
  network interface stanzas in the container's :file:`/etc/network/interfaces`
  file, by default with DHCP configuration. This will happen only on the
  initialization of the new container, when a given LXC container has multiple
  network interfaces defined in its configuration file.

- [debops.ansible_plugins] A new ``ldap_attrs`` Ansible module has been added
  to the role. It's a replacement for the ``ldap_attr`` core Ansible module,
  that's more in line with the ``ldap_entry`` module. Used by the
  :ref:`debops.slapd` and :ref:`debops.ldap` roles to manage the LDAP directory
  contents.

- The DebOps project has been registered `in the IANA Private Enterprise
  Numbers`__ registry, with PEN number ``53622``. The project documentation
  contains :ref:`an OID registry <debops_oid_registry>` to track custom LDAP
  schemas, among other things.

  .. __: https://www.iana.org/assignments/enterprise-numbers/enterprise-numbers

- A new ``bootstrap-ldap.yml`` Ansible playbook can be used to bootstrap
  Debian/Ubuntu hosts with LDAP support enabled by default. The playbook will
  configure only the services required for secure LDAP access (PKI, SSH,
  PAM/NSS), the rest should be configured using the common playbook.

- [debops.apt][debops.unattended_upgrades] Systems with the End of Life Debian
  releases (``wheezy``) installed will be configured to use the Debian Archive
  repository as the main APT sources instead of the normal Debian repository
  mirrors. These releases have been moved out of the main repositories and are
  not fully available through normal means. The periodic updates of the APT
  archive repositories on these systems will be disabled since the EOL releases
  no longer receive updates.

  The Debian LTS release (``jessie``) APT repository sources will use only the
  main and security repositories, without updates or backports. See the
  `information about the Debian LTS support`__ for more details.

  .. __: https://wiki.debian.org/LTS

- [debops.resources] New :ref:`resources__ref_commands` variables can be used
  to define simple shell commands or scripts that will be executed at the end
  of the :ref:`debops.resources` role. Useful to start new services, but it
  shouldn't be used as a replacement for a fully-fledged Ansible roles.

- [debops.sudo] The role is now integrated with the :ref:`debops.ldap` Ansible
  role and can configure the :command:`sudo` service to read ``sudoers``
  configuration from the LDAP directory.

- [debops.users] The role can now configure UNIX accounts with access
  restricted to SFTP operations (SFTPonly) with the new ``item.chroot``
  parameter. This is a replacement for the ``debops.sftpusers`` role.

- Support for Ansible Collections managed by the `Mazer`__ Content Manager has
  been implemented in the repository. Ansible Collections will be usable after
  June 2019, when support for them is enabled in the Ansible Galaxy service.

  .. __: https://github.com/ansible/mazer

Changed
~~~~~~~

- Updates of upstream application versions:

  - [debops.gitlab] The role will install GitLab 11.10 on supported platforms
    (Debian Buster, Ubuntu Bionic), existing installations will be upgraded.

  - [debops.phpipam] The relevant inventory variables have been renamed, check
    the :ref:`upgrade_notes` for details. The role now uses the upstream
    phpIPAM repository and it installs version 1.3.2.

  - [debops.php] Because of the PHP 7.0 release status changed to `End of life`__
    at the beginning of 2019, Ondřej Surý APT repository with PHP 7.2 packages
    will be enabled by default on Debian Jessie and Stretch as well as Ubuntu
    Trusty and Xenial. Existing :ref:`debops.php` installations shouldn't be
    affected, but the role will not try to upgrade the PHP version either.
    Users should consider upgrading the packages manually or reinstalling
    services from scratch with the newer version used by default.

    .. __: https://secure.php.net/supported-versions.php

  - [debops.rstudio_server] The supported version has been updated to
    v1.2.1335. The role no longer installs ``libssl1.0.0`` from Debian Jessie
    on Debian Stretch, since the current version of the RStudio Server works in
    the default Stretch environment. The downloaded ``.deb`` package will be
    verified using the RStudio Inc. GPG signing key before installation.

  - [debops.docker_gen] The docker-gen version that this role installs by
    default has been updated to version 0.7.4. This release notably adds IPv6
    and docker network support.

- [debops.lxc] The :command:`lxc-prepare-ssh` script will read the public SSH
  keys from specific files (``root`` key file, and the ``$SUDO_USER`` key file)
  and will not accept any custom files to read from, to avoid possible security
  issues. Each public SSH key listed in the key files is validated before being
  added to the container's ``root`` account.

  The :command:`lxc-new-unprivileged` script will similarly not accept any
  custom files as initial LXC container configuration to fix any potential
  security holes when used via :command:`sudo`. The default LXC configuration
  file used by the script can be configured in :file:`/etc/lxc/lxc.conf`
  configuration file.

- [debops.gitlab] The GitLab playbook will import the
  :ref:`debops.docker_registry` playbook to ensure that configuration related
  to Docker Registry defined in the GitLab service is properly applied during
  installation/management.

- [debops.php] The PHP version detection has been redesigned to use the
  :command:`apt-cache madison` command to find the available versions. The role
  will now check the current version of the ``php`` APT package to select the
  available stable PHP version. This unfortunately breaks support for the
  ``php5`` packages, but the ``php5.6`` packages from Ondřej Surý APT
  repository work fine.

- [debops.mariadb_server] The MariaDB user ``root`` is no longer dropped. This
  user is used for database maintenance and authenticates using the
  ``unix_auth`` plugin. However, DebOps still maintains and sets a password for
  the ``root`` UNIX account, stored in the :file:`/root/.my.cnf` config file.

- The :ref:`debops.cron` role will be applied much earlier in the
  ``common.yml`` playbook because the :ref:`debops.pki` role depends on
  presence of the :command:`cron` daemon on the host.

- [debops.netbase] The role will be disabled by default in Docker containers.
  In this environment, the :file:`/etc/hosts` file is managed by Docker and
  cannot be modified from inside of the container.

- [debops.owncloud] The role will not perform any tasks related to
  :command:`occ` command if the automatic setup is disabled in the
  :envvar:`owncloud__autosetup` variable. In this mode, the :command:`occ`
  tasks cannot be performed by the role because the ownCloud/Nextcloud
  installation is not finished. The users are expected to perform necessary
  tasks themselves if they decide to opt-out from the automatic configuration.

- [debops.slapd] The role has been redesigned from the ground up, with support
  for N-Way Multi-Master replication, custom LDAP schemas, Password Policy and
  other functionality. The role uses custom ``ldap_attrs`` Ansible module
  included in the :ref:`debops.ansible_plugins` role for OpenLDAP management.

  The OpenLDAP configuration will definitely break on existing installations.
  It's best to set up a new OpenLDAP server (or replicated cluster) and import
  the LDAP directory to it afterwards. See :ref:`role documentation
  <debops.slapd>` for more details.

- [debops.nullmailer][debops.postfix] The :file:`/etc/mailname` configuration
  file will contain the DNS domain of a host instead of the FQDN address. This
  will result in the mail senders that don't specify the domain part to have
  the DNS domain, instead of the full host address, added by the Mail Transport
  Agent. This configuration should work better in clustered environments, where
  there is a central mail hub/MX that receives the mail and redirects it.

- [debops.root_account] If the :ref:`debops.ldap` Ansible role has been applied
  on a host, the :ref:`debops.root_account` role will use the UID/GID ranges
  defined by it, which include UIDs/GIDs used in the LDAP directory, to define
  subUID/subGID range of the ``root`` account. This allows usage of the LDAP
  directory as a source of UNIX accounts and groups in unprivileged containers.
  Existing systems will not be changed.

- [debops.system_groups] If the LDAP support is enabled on a host via the
  :ref:`debops.ldap` role, the UNIX system groups created by the
  :ref:`debops.system_groups` role by default will use a ``_`` prefix to make
  them separate from any LDAP-based groups of the same name. Existing
  installations should be unaffected, as long as the updated
  :ref:`debops.system_groups` role was applied before the :ref:`debops.ldap`
  role.

- [debops.sshd] The access control based on UNIX groups defined in the
  :file:`/etc/ssh/sshd_config` file has been removed. Instead, the OpenSSH
  server uses the PAM access control configuration, managed by the
  :ref:`debops.pam_access` Ansible role, to control access by
  users/groups/origins. OpenSSH service uses its own access control file,
  separate from the global :file:`/etc/security/access.conf` file.

- [debops.sshd] The role will enable client address resolving using DNS by
  setting the ``UseDNS yes`` option in OpenSSH server configuration. This
  parameter is disabled by default in Debian and upstream, however it is
  required for the domain-based access control rules to work as expected.

- [debops.sshd] When the LDAP support is configured on a host by the
  :ref:`debops.ldap` role, the :ref:`debops.sshd` role will use the resulting
  infrastructure to connect to the LDAP directory and create the ``sshd`` LDAP
  account object for each host, used for lookups of the SSH keys in the
  directory. The SSH host public keys will be automatically added or updated in
  the LDAP device object to allow for centralized generation of the
  ``~/.ssh/known_hosts`` files based on the data stored in LDAP.

  The role will no longer create a separate ``sshd-lookup`` UNIX account to
  perform LDAP lookups; the existing ``sshd`` UNIX account will be used
  instead. The :command:`ldapsearch` command used for lookups will default to
  LDAP over TLS connections instead of LDAPS.

- [deops.unattended_upgrades] The packages from the ``stable-updates`` APT
  repository section will be automatically upgraded by default, the same as the
  packages from Debian Security repository. This should cover important
  non-security related upgrades, such as timezone changes, antivirus database
  changes, and similar.

- [debops.php] The role will install the :command:`composer` command from the
  upstream GitHub repository on older OS releases, including Debian Stretch
  (current Stable release). This is due to incompatibility of the ``composer``
  APT package included in Debian Stretch and PHP 7.3.

  The custom ``composer`` command installation tasks have been removed from the
  :ref:`debops.roundcube` and :ref:`debops.librenms` roles, since
  :ref:`debops.php` will take care of the installation.

- [debops.users][debops.root_account] Management of the ``root`` dotfiles has
  been removed from the :ref:`debops.users` role and is now done in the
  :ref:`debops.root_account` role, using the :command:`yadm` script. Users
  might need to clean out the existing dotfiles if they were managed as
  symlinks, otherwise :command:`yadm` script will not be able to correctly
  deploy the new dotfiles.

  The management of the user dotfiles in the :ref:`debops.users` role has been
  redesigned and now uses the :command:`yadm` script to perform the actual
  deployment. See :ref:`debops.yadm` for details about installing the script
  and creating local dotfile mirrors. The :ref:`users__ref_accounts` variable
  documentation contains examples of new dotfile definitions.

- [debops.users] The role now uses the ``libuser`` library via the Ansible
  ``group`` and ``user`` modules to manage local groups and accounts. This
  should avoid issues with groups and accounts created in the LDAP user/group
  ranges.

  The ``libuser`` library by default creates home directories with ``0700``
  permissions, which is probably too restrictive. Because of that, the role
  will automatically change the home directory permissions to ``0751`` (defined
  in the :envvar:`users__default_home_mode` variable). This also affects
  existing UNIX accounts managed by the role; the mode can be overriden using
  the ``item.home_mode`` parameter.

- [debops.users] The ``users__*_resources`` variables have been reimplemented
  as the ``item.resources`` parameter of the ``users__*_accounts`` variables.
  This removes the unnecessary split between user account definitions and
  definitions of their files/directories.

- Bash scripts and ``shell``/``command`` Ansible modules now use relative
  :command:`bash` interpreter instead of an absolute :file:`/bin/bash`. This
  should help make the DebOps roles more portable, and prepare the project for
  the merged :file:`/bin` and :file:`/usr/bin` directories in a future Debian
  release.

- [debops.unattended_upgrades] If automatic reboots are enabled, VMs will not
  reboot all at the same time to avoid high load on the hypervisor host.
  Instead they will reboot at a particular minute in a 15 minute time window.
  For each host, a random but random-but-idempotent time is chosen.
  For hypervisor hosts good presets cannot be picked. You should ensure that
  hosts don’t reboot at the same time by defining different reboot times in
  inventory groups.

Removed
~~~~~~~

- [debops.auth] The :file:`/etc/ldap/ldap.conf` file configuration,
  :command:`nslcd` service configuration and related variables have been
  removed from the :ref:`debops.auth` role. This functionality is now available
  in the :ref:`debops.ldap` and :ref:`debops.nslcd` roles, which manage the
  client-side LDAP support.

- [debops.rstudio_server] The role will no longer install the historical
  ``libssl1.0.0`` APT package on Debian Stretch to support older RStudio Server
  releases. You should remove it on the existing installations after RStudio
  Server is upgraded to the newest release.

- The ``debops.sftpusers`` Ansible role has been removed. Its functionality is
  now implemented by the :ref:`debops.users` role, custom bind mounts can be
  defined using the :ref:`debops.mount` role.

- The ``debops.bootstrap`` Ansible role has been removed. Its replacement is
  the :ref:`debops.system_users` which is used to manage system administrator
  accounts, via the ``common.yml`` playbook and the bootstrap playbooks.

Fixed
~~~~~

- [debops.redis_server] Use the :file:`redis.conf` file to lookup passwords via
  the :command:`redis-password` script. This file has the ``redis-auth`` UNIX
  group and any accounts in this group should now be able to look up the Redis
  passwords correctly.

- [debops.slapd] The role will check if the X.509 certificate and the private
  key used for TLS communication were correctly configured in the OpenLDAP
  server. This fixes an issue where configuration of the private key and
  certificate was not performed at all, without any actual changes in the
  service, with subsequent task exiting with an error due to misconfiguration.

- [debops.lvm] Make sure a file system is created by default when the ``mount``
  parameter is defined in the :envvar:`lvm__logical_volumes`.

- [debops.lvm] Stop and disable ``lvm2-lvmetad.socket`` systemd unit when
  disabling :envvar:`lvm__global_use_lvmetad` to avoid warning message when
  invoking LVM commands.

- [debops.authorized_keys] Set the group for authorized_keys files to the
  primary group of the user instead of the group with the same name as the
  user. This is important because otherwise the readonly mode of the role does
  not work when the primary group of a user has a different name then the
  username.

Security
~~~~~~~~

- [debops.php] Ondřej Surý `created new APT signing keys`__ for his Debian APT
  repository with PHP packages, due to security concerns. The :ref:`debops.php`
  role will remove the old APT GPG key and add the new one automatically.

  .. __: https://www.patreon.com/posts/dpa-new-signing-25451165


`debops v0.8.1`_ - 2019-02-02
-----------------------------

.. _debops v0.8.1: https://github.com/debops/debops/compare/v0.8.0...v0.8.1

Added
~~~~~

- New DebOps roles:

  - :ref:`debops.redis_server` and :ref:`debops.redis_sentinel` roles, that
    replace the existing ``debops.redis`` Ansible role. The new roles support
    multiple Redis and Sentinel instances on a single host.

  - :ref:`debops.freeradius`, an Ansible role that can be used to manage
    FreeRADIUS service, used in network management.

  - :ref:`debops.dhcp_probe`, can be used to install and configure
    :command:`dhcp_probe` service, which passively detects rogue DHCP servers.

  - :ref:`debops.mount`, the role allows configuration of :file:`/etc/fstab`
    entries for local devices, bind mounts and can be used to create or modify
    directories, to permit access to resources by different applications. The
    role is included by default in the ``common.yml`` playbook.

- [debops.users] The role can now configure ACL entries of the user home
  directories using the ``item.home_acl`` parameter. This can be used for more
  elaborate access restrictions.

- [debops.root_account] The role will reserve a set of UID/GID ranges for
  subordinate UIDs/GIDs owned by the ``root`` account (they are not reserved by
  default). This can be used to create unprivileged LXC containers owned by
  ``root``. See the release notes for potential issues on existing systems.

- [debops.root_account] You can now configure the state and contents of the
  :file:`/root/.ssh/authorized_keys` file using the :ref:`debops.root_account`
  role, with support for global, per inventory group and per host SSH keys.

- DebOps roles are now tagged with ``skip::<role_name>`` Ansible tags. You can
  use these tags to skip roles without any side-effects; for example
  "<role_name>/env" sub-roles will still run so that roles that depend on them
  will work as expected.

- [debops.ifupdown] The role will now generate configuration for the
  :ref:`debops.sysctl` role and use it in the playbook as a dependency, to
  configure kernel parameters related to packet forwarding on managed network
  interfaces. This functionality replaces centralized configuration of packet
  forwarding on all network interfaces done by the :ref:`debops.ferm` role.

- [debops.lxc] New :command:`lxc-hwaddr-static` script can be used to easily
  generate random but predictable MAC addresses for LXC containers.

  The script can be run manually or executed as a "pre-start" LXC hook to
  configure static MAC addresses automatically - this usage is enabled by
  default via common LXC container configuration.

- The `lxc_ssh.py <https://github.com/andreasscherbaum/ansible-lxc-ssh>`__
  Ansible connection plugin is now included by default in DebOps. This
  connection plugin can be used to manage remote LXC containers with Ansible
  via SSH and the :command:`lxc-attach` command. This requires connection to
  the LXC host and the LXC container via the ``root`` account directly, which
  is supported by the DebOps playbooks and roles.

- [debops.lxc] The role can now manage LXC containers, again. This time the
  functionality is implemented using the ``lxc_container`` Ansible module
  instead of a series of shell tasks. By default unprivileged LXC containers
  will be created, but users can change all parameters supported by the module.

- [debops.lxc] The role will now configure a ``lxcbr0`` bridge with internal
  DNS/DHCP server for LXC containers, using the ``lxc-net`` service. With this
  change, use of the :ref:`debops.ifupdown` role to prepare a default bridge
  for LXC containers is not required anymore.

- [debops.netbase] When a large number of hosts is defined for the
  :file:`/etc/hosts` database, the role will switch to generating the file
  using the ``template`` Ansible module instead of managing individual lines
  using the ``lineinfile`` module, to make the operation faster. As a result,
  custom modifications done by other tools in the host database will not be
  preserved.

- [debops.netbase] The role can now configure the hostname in the
  :file:`/etc/hostname` file, as well as the local domain configuration in
  :file:`/etc/hosts` database.

- Ansible roles included in DebOps are now checked using `ansible-lint`__ tool.
  All existing issues found by the script have been fixed.

  .. __: https://docs.ansible.com/ansible-lint/

- The hosts managed by the DebOps Vagrant environment will now use Avahi to
  detect multiple cluster nodes and generate host records in the
  :file:`/etc/hosts` database on these nodes. This allows usage of real DNS
  FQDNs and hostnames in the test environment without reliance on an external
  DHCP/DNS services.

- [debops.php] The role will install the ``composer`` APT package on Debian
  Stretch, Ubuntu Xenial and their respective newer OS releases.

- You can use the :command:`make versions` command in the root of the DebOps
  monorepo to check currently "pinned" and upstream versions of third-party
  software installed and managed by DebOps, usually via :command:`git`
  repositories. This requires the :command:`uscan` command from the Debian
  ``devscripts`` APT package to be present.

Changed
~~~~~~~

- The :ref:`debops.root_account` role will be executed earlier in the
  ``common.yml`` Ansible playbook to ensure that the ``root`` UID/GID ranges
  are reserved without issues on the initial host configuration.

- [debops.lxc] The role will configure the default subUIDs and subGIDs for
  unprivileged LXC containers based on the configured subordinate UID/GID
  ranges for the ``root`` account.

- [debops.gitlab] The role will now install GitLab 10.8 by default, on Debian
  Stretch and Ubuntu Xenial. The 11.x release now requires Ruby 2.4+, therefore
  it will only be installed on newer OS releases (Debian Buster, Ubuntu
  Bionic).

- [debops.gitlab] The role has been updated to use Ansible local facts managed
  by the :ref:`debops.redis_server` Ansible role. Redis Server support has been
  removed from the GitLab playbook and needs to be explicitly enabled in the
  inventory for GitLab to be installed correctly. This will allow to select
  between local Server or Sentinel instance, to support clustered environments.

  Check the :ref:`upgrade_notes` for issues with upgrading Redis Server support
  on existing GitLab hosts.

- [debops.owncloud] The role will now use Ansible facts managed by the
  :ref:`debops.redis_server` role to configure Redis support.

- [debops.lxc] The :command:`lxc-prepare-ssh` script will now install SSH
  public keys from the user account that is running the script via
  :command:`sudo` instead of the system's ``root`` account, which is usually
  what you want to do if other people manage their own LXC containers on
  a host.

- Various filter and lookup Ansible plugins have been migrated from the
  playbook directory to the :ref:`debops.ansible_plugins` role. This role can
  be used as hard dependency in other Ansible roles that rely on these plugins.

- [debops.grub] The GRUB configuration has been redesigned, role now uses
  merged variables to make configuration via Ansible inventory or dependent
  role variables easier. The GRUB configuration is now stored in the
  :file:`/etc/default/grub.d/` directory to allow for easier integration with
  other software. See the :ref:`debops.grub` documentation for more details.

- [debops.grub] The user password storage path in :file:`secret/` directory has
  been changed to use the ``inventory_hostname`` variable instead of the
  ``ansible_fqdn`` variable. This change will force regeneration of password
  hashes in existing installations, but shouldn't affect host access (passwords
  stay the same).

- [debops.docker] If the Docker host uses a local nameserver, for example
  :command:`dnsmasq` or :command:`unbound`, Docker containers might have
  misconfigured DNS nameserver in :file:`/etc/resolv.conf` pointing to
  ``127.0.0.1``. In these cases, the :ref:`debops.docker` role will configure
  Docker to use the upstream nameservers from the host, managed by the
  ``resolvconf`` APT package.

  If no upstream nameservers are available, the role will not configure any
  nameserver and search parameters, which will tell Docker to use the Google
  nameservers.

- The test suite will now check POSIX shell scripts along with Bash scripts for
  any issues via the :command:`shellcheck` linter. Outstanding issues found in
  existing scripts have been fixed.

- [debops.librenms] The default dashboard in LibreNMS is changed from the
  :file:`pages/front/default.php` to :file:`pages/front/tiles.php` which allows
  for better customization.

- The order of the roles in the common playbook has been changed; the
  :ref:`debops.users` role will be applied before the :ref:`debops.resources`
  role to allow for resources owned by UNIX accounts/groups other than
  ``root``.

- [debops.gunicorn] The role depends on :ref:`debops.python` now to install the
  required packages. Please update your custom playbooks accordingly.

- [debops.lxc] The LXC configuration managed by the role will use the
  :command:`systemd` ``lxc@.service`` instances to manage the containers
  instead of using the :command:`lxc-*` commands directly. This allows the
  containers to be shut down properly without hitting a timeout and forced
  killing of container processes.

- [debops.ipxe] The role will no longer install non-free firmware by default.
  This is done to solve the connectivity issues with ``cdimage.debian.org``
  host.

- The hostname and domain configuration during bootstrapping is now done by the
  :ref:`debops.netbase` Ansible role. The default for this role is to remove
  the ``127.0.1.1`` host entry from the :file:`/etc/hosts` file to ensure that
  domain resolution relies on DNS.

  If you are using local domain configured in :file:`/etc/hosts` file, you
  should define the :envvar:`netbase__domain` variable in the Ansible inventory
  with your desired domain.

- [debops.netbase] The role is redesigned to use list variables instead of YAML
  dictionaries for the :file:`/etc/hosts` database. This allows for adding the
  host IPv4 and/or IPv6 addresses defined by Ansible facts when the custom
  local domain is enabled. See :ref:`netbase__ref_hosts` for details.
  The role has also been included in the ``common.yml`` playbook to ensure that
  the host database is up to date as soon as possible.

- [debops.resources] Changed behaviour of used groups for templating. Now all
  groups the host is in, will be used to search for template files.
  Read the documentation about :ref:`resources__ref_templates` for more details
  on templating with `debops`.

- [debops.dnsmasq] The role has been redesigned from the ground up with new
  configuration pipeline, support for multiple subdomains and better default
  configuration. See the :ref:`debops.dnsmasq` role documentation as well as
  the :ref:`upgrade_notes` for more details.

- [debops.owncloud] Drop support for Nextcloud 12.0 which is EOF. Add support
  for Nextcloud 14.0 and 15.0 and make Nextcloud 14.0 the default Nextcloud
  version.

- The ``debops`` Python package has dropped the hard dependency on Ansible.
  This allows DebOps to be installed in a separate environment than Ansible,
  allowing for example to mix Homebrew Ansible with DebOps from PyPI on macOS.
  The installation instructions have also been updated to reflect the change.

- The :command:`debops-init` script will now generate new Ansible inventory
  files using the hostname as well as a host FQDN to better promote the use of
  DNS records in Ansible inventory.

Fixed
~~~~~

- [debops.kmod] The role should now work correctly in Ansible ``--check`` mode
  before the Ansible local fact script is installed.

- [debops.sysctl] The role should correctly handle nested lists in role
  dependent variables, which are now flattened before being passed to the
  configuration filter.

- [debops.grub] The role should now correctly revert custom patch to allow user
  authentication in :file:`/etc/grub.d/10_linux` script, when the user list is
  empty.

Removed
~~~~~~~

- The old ``debops.redis`` Ansible role has been removed. It has been replaced
  by the :ref:`debops.redis_server` and :ref:`debops.redis_sentinel` Ansible
  roles. The new roles use their own Ansible inventory groups, therefore they
  will need to be explicitly enabled to affect existing hosts.

  You can use the :ref:`debops.debops_legacy` Ansible role to clean up old
  configuration files, directories and diversions of ``debops.redis`` role from
  remote hosts.

- The ``ldap_entry`` and ``ldap_attr`` Ansible modules have been removed. They
  are now included in Ansible core, there's no need to keep a separate copy in
  the playbook.

- Support for :command:`dhcp_probe` has been removed from the
  :ref:`debops.dhcpd` Ansible role. It's now available as a separate
  :ref:`debops.dhcp_probe` role.

- [debops.ferm] Automated configuration of packet forwarding with ``FORWARD``
  chain rules and :command:`sysctl` configuration has been removed from the
  role. Per-interface packet forwarding is now configurable using the
  :ref:`debops.ifupdown` role, and you can still use the :ref:`debops.ferm` and
  :ref:`debops.sysctl` roles to design custom forwarding configuration.

  Support for this mechanism has also been removed from related roles like
  :ref:`debops.libvirtd` and :ref:`debops.lxc`.

- The ``ansible_local.root.flags`` and ``ansible_local.root.uuid`` local facts
  have been removed. They are replaced by ``ansible_local.tags`` and
  ``ansible_local.uuid`` local facts, respectively.

- The hostname and domain configuration has been removed from the
  ``debops.bootstrap`` role. This functionality is now handled by the
  :ref:`debops.netbase` role, which has been included in the bootstrap
  playbook. The relevant inventory variables have been renamed, check the
  :ref:`upgrade_notes` for details.

- The ``resources__group_name`` variable has been removed in favor of using
  all the groups the current hosts is in. This change has been reflected in the
  updated variable ``resources__group_templates``.


`debops v0.8.0`_ - 2018-08-06
-----------------------------

.. _debops v0.8.0: https://github.com/debops/debops/compare/v0.7.2...v0.8.0

Added
~~~~~

- New DebOps roles:

  - :ref:`debops.netbase`: manage local host and network database in
    :file:`/etc/hosts` and :file:`/etc/networks` files.

  - :ref:`debops.sudo`: install and manage :command:`sudo` configuration on
    a host. The role is included in the ``common.yml`` playbook.

  - :ref:`debops.system_groups`: configure UNIX system groups used on DebOps
    hosts. The role is included in the ``common.yml`` playbook.

  - :ref:`debops.debops_legacy`: clean up legacy files, directories, APT
    packages or :command:`dpkg-divert` diversions created by DebOps but no
    longer used. This role needs to be executed manually, it's not included in
    the main playbook.

  - :ref:`debops.python`: manage Python environment, with support for multiple
    Python versions used at the same time. The role is included in the
    ``common.yml`` playbook.

  - Icinga 2 support has been implemented with :ref:`debops.icinga`,
    :ref:`debops.icinga_db` and :ref:`debops.icinga_web` Ansible roles.

- [debops.users] Selected UNIX accounts can now be configured to linger when
  not logged in via the ``item.linger`` parameter. This allows these accounts
  to maintain long-running services when not logged in via their own private
  :command:`systemd` instances.

- [debops.sudo] You can now manage configuration files located in the
  :file:`/etc/sudoers.d/` directory using :ref:`sudo__*_sudoers <sudo__ref_sudoers>`
  inventory variables, with multiple level of conditional options.

- [debops.ntp] The OpenNTPD service will now properly integrate the
  :command:`ifupdown` hook script with :command:`systemd`. During boot, NTP
  daemon will be started once network interfaces are configured and will not
  restart multiple times on each network interface change.

- [debops.resources] The role can now generate custom files using templates,
  based on a directory structure. See :ref:`resources__ref_templates` for more
  details.

- [debops.nginx] A ``default`` set of SSL ciphers can be specified using the
  :envvar:`nginx_default_ssl_ciphers` variable. This disables the
  ``ssl_ciphers`` option in the :command:`nginx` configuration and forces the
  server to use the defaults provided by the OS.

- [debops.dhparam] The role will set up a :command:`systemd` timer to
  regenerate Diffie-Hellman parameters periodically if it's available. The
  timer will use random delay time, up to 12h, to help with mass DHparam
  generation in multiple LXC containers/VMs.

- The DebOps installation now depends on the `dnspython`__ Python library. This
  allows usage of the ``dig`` Ansible lookup plugin in DebOps roles to gather
  data via DNS SRV records.

  .. __: http://www.dnspython.org/

- The DebOps installation now depends on the `future`__ Python library which
  provides compatibility between Python 2.7 and Python 3.x environments. It is
  currently used in the custom Ansible filter plugin provided by DebOps, but
  its use will be extended to other scripts in the future to make the code more
  readable.

  .. __: http://python-future.org/

Changed
~~~~~~~

- The :command:`editor` alternative symlink configuration has been moved from
  the ``debops.console`` role to the :ref:`debops.apt_install` role which also
  installs :command:`vim` by default.

- The configuration of automatic removal of APT packages installed via
  ``Recommends:`` or ``Suggests:`` dependencies has been moved from the
  :ref:`debops.apt` role to the :ref:`debops.apt_mark` role which more closely
  reflects its intended purpose. Variable names and their default values
  changed; see the :ref:`upgrade_notes` for more details.

- [debops.owncloud] Support Nextcloud 13 and partially ownCloud 10. Nextcloud
  11 and ownCloud 9.1 are EOL, you should update. The role can help you with
  the update to ensure that everything works smoothly with the new versions.
  Currently, the role can not do the update for you.

- [debops.sshd] The role will now check the :ref:`debops.system_groups` Ansible
  local facts to define what UNIX groups are allowed to connect to the host via
  the SSH service.

- [debops.nodejs] The NPM version installed by the role from GitHub is changed
  from ``v5.4.2`` to ``latest`` which seems to be an equivalent of a stable
  branch.

- Some of the existing DebOps Policies and Guidelines have been reorganized and
  the concept of DebOps Enhancement Proposals (DEPs) is introduced, inspired by
  the `Python Enhancement Proposals`__.

.. __: https://www.python.org/dev/peps/pep-0001/

- [debops.ifupdown] The :ref:`debops.kmod` role is added as a dependency. The
  :ref:`debops.ifupdown` role will generate :command:`modprobe` configuration
  based on the type of configured network interfaces (bridges, VLANs, bonding)
  and the kernel modules will be automatically loaded if missing.

- [debops.nodejs] Recent versions of NPM `require NodeJS 6.0.0+`__ and don't
  work with other releases. Because of that the newest NPM release is not
  installable on hosts that use NodeJS packages from older OS releases.

  .. __: https://github.com/npm/npm/issues/20425

  The 'debops.nodejs' role will install NPM v5.10.0 version in this case to
  allow NPM to work correctly - on Debian Jessie, Stretch and Ubuntu Xenial.
  Otherwise, a NPM from the ``latest`` branch will be installed, as before.

- [debops.nodejs] Instead of NodeJS 6.x release, the role will now install
  NodeJS 8.x release upstream APT packages by default. This is due to the
  NodeJS 6.x release `switching to a Maintenance LTS mode`__. NodeJS 8.x will
  be supported as a LTS release until April 2019.

  .. __: https://github.com/nodejs/Release

- [debops.nodejs] The role will install upstream NodeSource APT packages by
  default. This is due to `no security support in Debian Stable`__, therefore
  an upstream packages should be considered more secure. The upstream NodeJS
  packages include a compatible NPM release, therefore it won't be separately
  installed from GitHub.

  .. __: https://www.debian.org/releases/stretch/amd64/release-notes/ch-information.en.html#libv8

  The existing installations shouldn't be affected, since the role will select
  OS/upstream package versions based on existing Ansible local facts.

- [debops.gitlab] Redesign the GitLab version management to read the versions
  of various components from the GitLab repository files instead of managing
  them manually in a YAML dictionary. The new :envvar:`gitlab__release`
  variable is used to specify desired GitLab version to install/manage.

- [debops.gitlab] The :command:`gitaly` service will be installed using the
  ``git`` UNIX account instead of ``root``. Existing installations might
  require additional manual cleanup; see the :ref:`upgrade_notes` for details.

- [debops.gitlab] The role now supports installation of GitLab 10.7.

- [debops.gitlab] The usage of :envvar:`gitlab__fqdn` variable is revamped
  a bit - it's now used as the main variable that defines the GitLab
  installation FQDN. You might need to update the Ansible inventory if you
  changed the value of the ``gitlab_domain`` variable used previously for this
  purpose.

- [debops.lxc] Redesign system-wide LXC configuration to use list of YAML
  dictionaries merged together instead of custom Jinja templates.

- [debops.lxc] Add :command:`lxc-prepare-ssh` script on the LXC hosts that can
  be used to install OpenSSH and add the user's SSH authorized keys inside of
  the LXC containers. This is a new way to prepare the LXC containers for
  Ansible/DebOps management that doesn't require custom LXC template scripts
  and can be used with different LXC container types.

- [debops.core] The role will add any new administrator accounts to the list of
  existing admin accounts instead of replacing them in the Ansible local fact
  script. This should allow for multiple administrators to easily coexist and
  run the DebOps playbooks/roles from their own accounts without issues.

- [debops.mariadb_server] [debops.mariadb] The MariaDB/MySQL server and client
  will now use the ``utf8mb4`` encoding by default instead of the ``utf8``
  which is an internal MySQL character encoding. This might impact existing
  databases, see the :ref:`upgrade_notes` for details.

- [debops.unattended_upgrades] On hosts without a domain set, the role enabled
  all upgrades, not just security updates. This will not happen anymore, the
  security updates are enabled everywhere by default, you need to enable all
  upgrades specifically via the :envvar:`unattended_upgrades__release`
  variable.

- The :command:`debops` script can now parse multiple playbook names specified
  in any order instead of just looking at the first argument passed to it.

Removed
~~~~~~~

- [debops.apt_install], [debops.auth]: don't install the ``sudo`` package by
  default, this is now done via a separate :ref:`debops.sudo` role to easily
  support switching to the ``sudo-ldap`` APT package.

- [debops.console] Remove support for copying custom files from the role. This
  functionality is covered better by the :ref:`debops.resources` role.

- [debops.console] Remove support for managing entries in the
  :file:`/etc/hosts` database. This is now covered by the :ref:`debops.netbase`
  Ansible role.

- [debops.auth] Remove configuration of UNIX system groups and accounts in the
  ``admins`` UNIX group. This is now done by the :ref:`debops.system_groups`
  Ansible role.

- [debops.bootstrap] The :command:`sudo` configuration has been removed from
  the ``debops.bootstrap`` role. The ``bootstrap.yml`` playbook now includes
  the :ref:`debops.sudo` role which configures :command:`sudo` service.

- [debops.bootstrap] The UNIX system group management has been removed from the
  role, the ``bootstrap.yml`` playbook now uses the :ref:`debops.system_groups`
  role to create the UNIX groups used by DebOps during bootstrapping.

- [debops.bootstrap] Remove management of Python packages from the role. The
  ``bootstrap.yml`` playbook uses the :ref:`debops.python` role to configure
  Python support on the host.

- [debops.lxc] Remove support for direct LXC container management from the
  role. This functionality is better suited for other tools like
  :command:`lxc-*` set of commands, or the Ansible ``lxc_container`` module
  which should be used in custom playbooks. The 'debops.lxc' role focus should
  be configuration of LXC support on a host.

- [debops.lxc] Remove custom LXC template support. The LXC containers can be
  created by the normal templates provided by the ``lxc`` package, and then
  configured using DebOps roles as usual.

- [debops.postgresql_server] The tasks that modified the default ``template1``
  database and its schema have been removed to make the PostgreSQL installation
  more compatible with applications packaged in Debian that rely on the
  PostgreSQL service. See the relevant commit for more details. Existing
  installations shouldn't be affected.


`debops v0.7.2`_ - 2018-03-28
-----------------------------

.. _debops v0.7.2: https://github.com/debops/debops/compare/v0.7.2...v0.7.2

Fixed
~~~~~

- Add missing ``python-ldap`` dependency as an APT package in the Dockerfile.


`debops v0.7.1`_ - 2018-03-28
-----------------------------

.. _debops v0.7.1: https://github.com/debops/debops/compare/v0.7.0...v0.7.1

Added
~~~~~

- New DebOps roles:

  - :ref:`debops.ansible`: install Ansible on a Debian/Ubuntu host using
    Ansible. The :ref:`debops.debops` role now uses the new role to install
    Ansible instead of doing it directly.

  - :ref:`debops.apt_mark`: set install state of APT packages (manual/auto) or
    specify that particular packages should be held in their current state.
    The role is included in the ``common.yml`` playbook.

  - :ref:`debops.kmod`: manage kernel module configuration and module loading
    at boot time. This role replaces the ``debops-contrib.kernel_module`` role.

  - The ``debops-contrib.etckeeper`` role has been integrated into DebOps as
    :ref:`debops.etckeeper`. The new role is included in the ``common.yml``
    playbook.

- [debops.ifupdown] The role has new tasks that manage custom hooks in other
  services. First hook is :ref:`ifupdown__ref_custom_hooks_filter_dhcp_options`
  which can be used to selectively apply DHCP options per network interface.

Changed
~~~~~~~

- [debops.lxc] The role will now generate the ``lxc-debops`` LXC template
  script from different templates, based on an OS release. This change should
  help fix the issues with LXC container creation on Debian Stretch.

- The test suite used on Travis-CI now checks the syntax of the YAML files, as
  well as Python and shell scripts included in the repository. The syntax is
  checked using the :command:`yamllint`, :command:`pycodestyle` and
  :command:`shellcheck` scripts, respectively. Tests can also be invoked
  separately via the :command:`make` command.

- [debops.etherpad] The role can now autodetect and use a PostgreSQL database
  as a backend database for Etherpad.

- [debops.pki] The X.509 certificate included in the default ``domain`` PKI
  realm will now have a SubjectAltName wildcard entry for the host's FQDN. This
  should allow for easy usage of services related to a particular host in the
  cluster over encrypted connections, for example host monitoring, service
  discovery, etc. which can be now published in the DNS zone at
  ``*.host.example.org`` resource records.

- [debops.pki] The role now supports Let's Encrypt ACMEv2 API via the
  `acme-tiny`__ Python script. The existing PKI realms will need to be
  re-created or updated for the new API to work, new PKI realms should work out
  of the box. Check the :ref:`upgrade_notes` for more details.

- [debops.proc_hidepid], [debops.lxc] The roles now use a static GID ``70`` for
  the ``procadmins`` group to synchronize the access permissions on a host and
  inside the LXC containers. You will need to remount the filesystems, restart
  services and LXC containers that rely on this functionality.

- [debops.sysctl] The configuration of the kernel parameters has been
  redesigned, instead of being based on YAML dictionaries, is now based on YAML
  lists of dictionaries and can be easily changed via Ansible inventory. You
  will need to update your inventory for the new changes to take effect, refer
  to the :ref:`role documentation <sysctl__ref_parameters>` for details.

- [debops.ferm] The role should now correctly detect what Internet Protocols
  are available on a host (IPv4, IPv6) and configure firewall only for the
  protocols that are present.

.. __: https://github.com/diafygi/acme-tiny

Fixed
~~~~~

- The :command:`debops` command will now generate the :file:`ansible.cfg`
  configuration file with correct path to the Ansible roles provided with the
  DebOps Python package.

- [debops.nginx] Fix a long standing bug in the role with Ansible failing
  during welcome page template generation with Jinja2 >= 2.9.4. It was related
  to `non-backwards compatible change in Jinja`__ that modified how variables
  are processed in a loop.

.. __: https://github.com/pallets/jinja/issues/659

Removed
~~~~~~~

- The ``debops-contrib.kernel_module`` Ansible role has been removed; it was
  replaced by the new :ref:`debops.kmod` Ansible role.

- [debops.ferm] The ``ferm-forward`` hook script in the
  :file:`/etc/network/if-pre-up.d/` directory has been removed (existing
  instances will be cleaned up). Recent changes in the :ref:`debops.ferm` role
  broke idempotency with the :ref:`debops.ifupdown` role, and it was determined
  that the functionality provided by the hook is no longer needed, recent OS
  releases should deal with it adequately.


`debops v0.7.0`_ - 2018-02-11
-----------------------------

.. _debops v0.7.0: https://github.com/debops/debops/compare/v0.6.0...v0.7.0

Added
~~~~~

- New Ansible roles have been imported from the ``debops-contrib``
  organization: ``apparmor``, ``bitcoind``, ``btrfs``, ``dropbear_initramfs``,
  ``etckeeper``, ``firejail``, ``foodsoft``, ``fuse``, ``homeassistant``,
  ``kernel_module``, ``kodi``, ``neurodebian``, ``snapshot_snapper``, ``tor``,
  ``volkszaehler``, ``x2go_server``. They are not yet included in the main
  playbook and still need to be renamed to fit with the rest of the
  ``debops.*`` roles.

- New DebOps roles:

  - :ref:`debops.sysfs`: configuration of the Linux kernel attributes through
    the :file:`/sys` filesystem. The role is not enabled by default.

  - :ref:`debops.locales`: configure localization and internationalization on
    a given host or set of hosts.

  - :ref:`debops.machine`: manage the :file:`/etc/machine-info` file,
    the :file:`/etc/issue` file and a dynamic MOTD.

  - :ref:`debops.proc_hidepid`: configure the ``/proc`` ``hidepid=`` options.

  - :ref:`debops.roundcube`: manage RoundCube Webmail application

  - :ref:`debops.prosody`: configure an xmpp server on a given host

  - :ref:`debops.sysnews`: manage System News bulletin for UNIX accounts

- You can now :ref:`use Vagrant <quick_start__vagrant>` to create an Ansible
  Controller based on Debian Stretch and use it to manage itself or other hosts
  over the network.

- You can now build an Ansible Controller with DebOps support as a Docker
  container. :ref:`Official Docker image <quick_start__docker>` is also
  available, automatically rebuilt on every commit.

- You can now install DebOps on `Arch Linux <https://www.archlinux.org/>`__
  using an included ``PKGBUILD`` file.

- Add new playbook, ``agent.yml``. This playbook is executed at the end of the
  main playbook, and contains applications or services which act as "agents" of
  other services. They may contact their parent applications to report about
  the state of the host they are executed on, therefore the agents are
  installed and configured at the end of the main playbook.

- [debops.libvirtd] The role can now detect if nested KVM is enabled in
  a particular virtual machine and install KVM support.

  [debops.nodejs] The :ref:`debops.nodejs` role can now install `Yarn
  <https://yarnpkg.com/>`_ package manager using its upstream APT repository
  (not enabled by default).

- DebOps roles and playbooks can now be tested using local or remote
  `GitLab CI <https://about.gitlab.com/>`_ instance, with Vagrant, KVM and LXC
  technologies and some custom scripts.

- DebOps roles and playbooks will be included in the Python packages released
  on PyPI. This will allow for easier installation of DebOps via :command:`pip`
  (no need to download the roles and playbooks separately) as well as simple
  stable releases. The DebOps monorepo can still be installed separately.

Changed
~~~~~~~

- [debops-tools] The :command:`debops-update` script will now install or
  update the DebOps monorepo instead of separate ``debops-playbooks`` and
  DebOps roles git repositories. Existing installations shouldn't be affected.

- [debops-tools] The :command:`debops` script will now include the DebOps
  monorepo roles and playbooks in the generated :file:`ansible.cfg`
  configuration. The monorepo roles and playbooks are preferred over the old
  ``debops-playbooks`` ones.

  The script is backwards compatible and should work correctly with or without
  the ``debops-playbooks`` repository and roles installed.

- The project repository is tested using :command:`pycodestyle` for compliance
  with Python's `PEP8 Style Guide <https://pep8.org/>`_.

- [debops.nodejs] The ``npm`` package has been removed from Debian Stable.
  The role will now install NPM using the GitHub source, unless upstream NodeJS is
  enabled, which includes its own NPM version.

- [debops.gunicorn] Update the role to work correctly on Debian Stretch and
  newer releases. The support for multiple :command:`gunicorn` instances using
  custom Debian scripts has been removed in Debian Stretch, therefore the role
  replaces it with its own setup based on :command:`systemd` instances.

- [debops.gitlab_runner] The GitLab Runner playbook is moved to the
  ``agent.yml`` playbook; it will be executed at the end of the main playbook
  and should that way include correct information about installed services.

- Improved Python 3 support in the DebOps scripts and throughout the
  playbooks/roles. DebOps should now be compatible with both Python versions.

Removed
~~~~~~~

- [DebOps playbooks] Remove the :file:`ipaddr.py` Ansible filter plugin, it is
  now included in the Ansible core distribution.

- [debops.console] Remove the ``locales`` configuration from the
  'debops.console' role, this functionality has been moved to the new
  'debops.locales' role. You will need to update the Ansible inventory
  variables to reflect the changes.

- [debops.console] Remove management of the :file:`/etc/issue` and
  :file:`/etc/motd` files from the ``debops.console`` role. That functionality
  is now available in the :ref:`debops.machine` role. You will need to update
  the Ansible inventory variables to reflect the changes.

- [debops.console] Management of the ``/proc`` ``hidepid=`` option has been
  moved to a new role, :ref:`debops.proc_hidepid`. You will need to update the
  Ansible inventory variables to reflect the changes.

- [debops.console] Management of the System News using the ``sysnews`` Debian
  package has been removed from the role; it's now available as a separate
  :ref:`debops.sysnews` Ansible role. You will need to update the Ansible
  inventory variables related to System News due to this changes.


debops v0.6.0 - 2017-10-21
--------------------------

Added
~~~~~

- Various repositories that comprise the DebOps project have been merged into
  a single monorepo which will be used as the main development repository.
  Check the :command:`git` log for information about older releases of DebOps
  roles and/or playbooks.
