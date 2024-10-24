.. Copyright (C) 2017-2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018-2022 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2017-2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _changelog:

Changelog
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <https://keepachangelog.com/en/1.0.0/>`__.

This file contains only general overview of the changes in the DebOps project.
The detailed changelog can be seen using :command:`git log` command.

You can read information about required changes between releases in the
:ref:`upgrade_notes` documentation.


`debops master`_ - unreleased
-----------------------------

.. _debops master: https://github.com/debops/debops/compare/v3.2.0...master

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.nixos` role with its corresponding playbook can be used to
  manage NixOS-based hosts. The role is not included in the main
  :file:`site.yml` playbook, which is focused on Debian/Ubuntu hosts.

- The :ref:`debops.influxdb2` role can be used to install and configure
  `InfluxDB v2.x`__ time-series database.

  .. __: https://www.influxdata.com/products/influxdb/

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- The role now supports `iterate_filter` for its LDAP configuration, allowing
  :command:`doveadm` commands to iterate over all users. Note that you might
  have to adjust the defaults for the :envvar:`dovecot__ldap_user_list_filter`
  variable if you use the :envvar:`dovecot__ldap_user_filter` variable.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Different file templates used in the role can now be overridden by the users
  with the DebOps template override system and the ``template_src`` lookup
  plugin.

:ref:`debops.resolved` role
'''''''''''''''''''''''''''

- The role will add a new entry in the :file:`/etc/services` database (using
  the :ref:`debops.etc_services` role) for the ``5355`` TCP and UDP ports,
  reserved for the `Link-Local Multicast Name Resolution`__. This should help
  with identification of unknown TCP/UDP ports of the listening services.

  .. __: https://en.wikipedia.org/wiki/Link-Local_Multicast_Name_Resolution

Changed
~~~~~~~

General
'''''''

- The :ref:`debops.root_account`, :ref:`debops.system_users` and
  :ref:`debops.users` roles are now able to handle the symlinked
  :file:`~/.ssh/authorized_keys` files correctly using optional ``follow``
  parameter.

- Harmonize all roles on `role::ROLE:pkgs` Ansible tag. The roles:

  - :ref:`debops.apparmor`
  - :ref:`debops.imapproxy`
  - :ref:`debops.owncloud`
  - :ref:`debops.roundcube`
  - :ref:`debops.rspamd`

  used `role::ROLE:pkg` previously.

- The DebOps CI pipeline in GitHub Actions is improved and will be executed on
  pull requests and pushes to test changes before merging them.

:ref:`debops.cryptsetup` role
'''''''''''''''''''''''''''''

- Make PBKDF configurable and already set Argon2id which is the new default of
  cryptsetup 2.4.0. See :envvar:`cryptsetup__pbkdf` for details.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- The role is now compatible with GitLab 17.x and newer releases.

- The runner registration method has changed, see the role documentation for
  details.

Fixed
~~~~~

General
'''''''

- The :ref:`debops.system_users` and the :ref:`debops.users` roles will add the
  dotfiles repository cloned by the ``root`` UNIX account in the
  :ref:`debops.yadm` role to the list of trusted :command:`git` repositories in
  the :file:`~/.gitconfig` configuration file of each user account managed by
  the role. This is needed to allow :command:`git` to clone local repositories
  not owned by the UNIX account, required by the mitigation of the
  `CVE-2022-24765`__ security vulnerability.

  .. __: https://github.blog/open-source/git/git-security-vulnerability-announced/#cve-2022-24765

- The :command:`debops` script will not try to download the required Ansible
  Collections during new project creation if the :command:`ansible-galaxy`
  command is not available in the user's ``$PATH``.

- The :ref:`tools/dist-upgrade.yml` playbook will not fail anymore during
  :file:`/etc/services` database assembly if no upgrade was performed.

:ref:`debops.apache` role
'''''''''''''''''''''''''

- Fixed an issue with the vhost ``state: "absent"`` parameter not working
  correctly when the ``enabled: False`` parameter was not set as well.

:ref:`debops.docker_gen` role
'''''''''''''''''''''''''''''

- Flattened the list of directories that are created by the ``file`` task. This
  should fix the issue of Ansible stopping during execution due to nested lists
  in the ``loop`` keyword.

:ref:`debops.dropbear_initramfs` role
'''''''''''''''''''''''''''''''''''''

- The role now supports both the old and the new location if the initramfs
  configuration files.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The role will restart the :command:`fail2ban` service instead of reloading
  it, which will ensure that the custom rules are re-added when the
  :command:`ferm` service is restarted.

- Fixed an issue with the role failing if the :envvar:`ferm__parsed_rules`
  variable is not defined correctly. The role will skip rule generation in such
  case instead of failing with the "AnsibleUndefined" error message.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Fixed conditional logic in a task which determines if the "autosetup"
  operation should be performed during Nextcloud/ownCloud installation.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- Fixed an issue with the ``vacuum_defer_cleanup_age`` option removal in
  PostgreSQL 16.x resulting in failed startup of the service. The option will
  be added only on supported PostgreSQL versions.

Removed
~~~~~~~

General
'''''''

- The ``volkszaehler`` (``debops-contrib``) role was removed because the role
  maintainer considers the application to be superseded by Grafana.
  See `Future of the project; The elephant in the room – Grafana`__.

  .. __: https://github.com/volkszaehler/volkszaehler.org/issues/819

- The ``bitcoind`` role was removed due to lack of interest by the role
  maintainer.

Security
~~~~~~~~

:ref:`debops.icinga` role
'''''''''''''''''''''''''

- The GPG key of the Icinga upstream APT repository `has been replaced`__ on
  2024-09-30. The role includes the new key which should be installed
  on the host on the next run. The old GPG key will not be removed
  automatically.

  .. __: https://icinga.com/blog/2024/08/26/icinga-package-repository-key-rotation-2024/


`debops v3.2.0`_ - 2024-09-16
-----------------------------

.. _debops v3.2.0: https://github.com/debops/debops/compare/v3.1.0...v3.2.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.debconf` Ansible role can be used to pre-configure APT
  packages which use the `debconf`__ configuration database and install them
  afterwards. The role is included near the end of the :file:`site.yml`
  playbook to allow of configuration of other needed services before the actual
  package installation.

  .. __: https://en.wikipedia.org/wiki/Debian_configuration_system

General
'''''''

- The :command:`debops` script can now log its operation to standard error and
  to the :command:`syslog` service. Use the ``--verbose`` or ``-v`` flag to
  enable log output on the console.

- Users can define "playbook sets" on the view level of the "modern" project
  directories. Playbook sets can be used as aliases to call multiple playbooks
  using a custom name. See :ref:`playbook_sets` documentation for more details.

- Users can now enable "read-only Fridays" functionality on a per project
  basis, to ensure that on Fridays, Ansible playbooks are run only in check
  mode, with ``--check`` and ``--diff`` arguments automatically added to the
  :command:`ansible-playbook` command options.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The role will import the :ref:`debops.secret` role during execution to get
  access to the :file:`secret/` directory. This permits use of stored passwords
  in Debconf answers configured via the :ref:`debops.apt_install` role.

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- The role can optionally ignore IP addresses on a network interface and use
  only specified ones for :command:`dnsmasq` configuration. This can help with
  Routing Advertisements issues on internal networks. See role documentation
  for more details.

:ref:`debops.pki` role
''''''''''''''''''''''

- Add support for defining per-realm UNIX environment variables set during
  :command:`pki-realm` script execution. These variables can be used to augment
  runtime environment, for example to define HTTP proxy to use inside internal
  networks with restricted access to the outside world.

:ref:`debops.rabbitmq_server` role
''''''''''''''''''''''''''''''''''

- The role can manage much more RabbitMQ internal structures - exchanges,
  queues, bindings between them, as well as vhost and user limits.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, support for the Debian Bullseye netboot
  installer has been updated to v11.12; the Debian Bookworm installer has been
  updated to v12.7.

General
'''''''

- DebOps now uses `pipx`__ as the preferred installation method. This allows
  for easier maintenance of the DebOps virtual environment.

  .. __: https://pipx.pypa.io/

:ref:`debops.elasticsearch` role
''''''''''''''''''''''''''''''''

- The role now supports new Elasticsearch v8.x password management mechanism.

- The role can now manage passwords in separate Elasticsearch clusters defined
  in one Ansible inventory.

  .. warning:: Due to this change, Elasticsearch passwords stored in the
               :file:`ansible/secret/` subdirectory will be read from a different
               location. If passwords are not moved to the new location, role
               will reset the Elasticsearch built-in users passwords
               automatically. This might result in data loss.

:ref:`debops.kibana` role
'''''''''''''''''''''''''

- The path to the password file stored in :file:`ansible/secret/` subdirectory
  is now configurable using a variable.

- The role uses new per-cluster Elasticsearch passwords by default. This is
  done using a separate :envvar:`kibana__elasticsearch_cluster_name` variable,
  which needs to be synchronized with the Elasticsearch configuration via
  Ansible inventory (Kibana can be installed separately from Elasticsearch).

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role supports integration with the :command:`systemd-resolved` DNS
  resolver. This permits use of the :command:`systemd-networkd` service to
  manage networking on the LXC host.

- LXC containers will be configured with AppArmor "unconfined" profile by
  default. This change allows startup of various services inside of the
  container without errors on Debian Bookwrom hosts.

:ref:`debops.lxd` role
''''''''''''''''''''''

- The role supports integration with the :command:`systemd-resolved` DNS
  resolver. This permits use of the :command:`systemd-networkd` service to
  manage networking on the LXD host.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The ``/index.html`` and ``/index.htm`` entries in the default ``try_files``
  configuration option have been replaced with the ``$uri/index.html`` entry.
  This change should ensure that any location not present on the server will
  return error 404 correctly, instead of falling back to the ``/index.html``
  file if it's present in the root of the website.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- The :command:`autopostgresqlbackup` script was modified to have separate set
  of options for the :command:`psql` command and the :command:`pg_dump`
  command. This permits the use of the ``--format=custom`` option in
  :command:`pg_dump` command, enabling more efficient database dumps.

- The extension of the backup files created by the
  :command:`autopostgresqlbackup` script can be configured via a default
  variable. This change might cause existing installations to change the file
  extension used during backups.

:ref:`debops.proc_hidepid` role
'''''''''''''''''''''''''''''''

- The role will check if the host is in the ``debops_service_libvirtd`` Ansible
  inventory group, or if the :ref:`debops.libvirtd` role was applied on the
  host and will change the ``hidepid=`` value to ``0`` to avoid issues with
  Polkit subsystem.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- The log rotation configuration for logs managed by :command:`rsyslog` now has
  an upper size limit of 1 GB to trigger the rotation. This should help in
  cases when these logs are growing rapidly, but the rotation period is too
  large to avoid filling up disk space.

:ref:`debops.zabbix_agent` role
'''''''''''''''''''''''''''''''

- The fact script now supports both the old Zabbix Agent, and the new Zabbix
  Agent 2 configuration files.

Fixed
~~~~~

:ref:`debops.dpkg_cleanup` role
'''''''''''''''''''''''''''''''

- Various YAML lists used in the package removal script will be sorted at Jinja
  level to avoid constand reordering of list elements during Ansible execution
  which makes the role not idempotent.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- Fixed an issue with the :file:`/etc/gitlab/ssl/` directory changing its mode
  from 0775 set by the role to 0755 set by the :command:`gitlab-ctl
  reconfigure` command, making the role not idempotent.

:ref:`debops.grub` role
'''''''''''''''''''''''

- Fixed an issue with the :file:`01_users` configuration file generating errors
  and resulting in an empty user section in the configuration generated by the
  :command:`update-grub` command.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- Fixed an issue with the :file:`ifup-allow-boot.service` :command:`systemd`
  unit not starting correctly on boot due to issues with the ``$`` character
  escaping.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role will by default disable NFtables integration within the
  :command:`lxc-net` script, configurable via a default variable. This fixes
  usage of LXC containers on Debian Bookworm with the :command:`ferm` service
  used by DebOps.

:ref:`debops.lxd` role
''''''''''''''''''''''

- Fixed an issue with the default LXD daemon preseed configuration by removing
  the unsupported ``managed`` parameter. This should allow the LXD daemon to be
  initialized correctly.

- Fixed an issue with the role trying to copy the source-built libraries when
  an APT-based installation is used. The role will check if the libraries exist
  before trying to copy them.

- Fixed an issue on Debian Bookworm where the :command:`lxd-apparmor-load`
  binary is not present where the APT-based LXD daemon expects it. The role
  will create a symlink for this binary when needed.

:ref:`debops.networkd` role
'''''''''''''''''''''''''''

- Do not restart the :command:`systemd-networkd` service if the role detects
  that the network stack is not managed by it. This should avoid the issue
  where the role playbook hanged on first run of the role on a host not managed
  by :command:`systemd-networkd` service.

:ref:`debops.ntp` role
''''''''''''''''''''''

- Fixed an issue with conditional check for Linux capabilities not being
  checked reliably to decide if NTP support should be enabled. The role should
  now correctly detect when Linux capabilities are enforced.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- List of log files which should be managed by the :command:`logrotate` service
  will be sorted to avoid constant reordering during role execution, which
  fixes role idempotency.

:ref:`debops.swapfile` role
'''''''''''''''''''''''''''

- Fixed an issue in the :command:`swapon` task conditional logic where the task
  could not be executed correctly when the swap file was missing.

- Ensure that the swap file is correctly disabled by the :command:`swapoff`
  command before being removed with the ``absent`` state.

Removed
~~~~~~~

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- Debian 9 (Stretch) has been removed from Debian mirrors, therefore the role
  will no longer offer support for installing Debian Stretch via PXE boot.


`debops v3.1.0`_ - 2023-11-29
-----------------------------

.. _debops v3.1.0: https://github.com/debops/debops/compare/v3.0.0...v3.1.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.metricbeat` role, part of the Elastic stack, can be used to
  install `Metricbeat`__, a service that can gather metrics and other non-log
  data from other services and send them to Elasticsearch for processing.

  .. __: https://www.elastic.co/beats/metricbeat

- The :ref:`debops.opensearch` role can be used to set up an unsecured,
  local-only installation of `OpenSearch`__. OpenSearch is a fork of
  Elasticsearch that continues to be released under a free software license.

  .. __: https://opensearch.org/

- The :ref:`debops.reboot` role can be used to reboot, forcefully or only if
  required, any DebOps host.

- The :ref:`debops.miniflux` role can install and manage Miniflux, a web-based,
  minimalistic feed reader written in Go.

- The :ref:`debops.systemd` role is included in the common playbook by default.
  It configures the :command:`systemd` system and service manager. Both
  system-wide, as well as user services configured globally can be managed with
  this role.

- The :ref:`debops.networkd` role can be used to configure the
  :command:`systemd-networkd` service, part of the :command:`systemd` project
  responsible for network interface configuration.

- The :ref:`debops.timesyncd` role is used to configure the
  :command:`systemd-timesyncd` service, a minimal SNTP/NTP client. The role is
  included in the :file:`layer/common.yml` playbook instead of the
  :ref:`debops.ntp` role to provide NTP support by default.

- The :ref:`debops.resolved` role is included in the :file:`layer/common.yml`
  playbook by default, replacing the :ref:`debops.resolvconf` role. It manages
  the :command:`systemd-resolved` service, a local DNS resolver.

- The :ref:`debops.bind` role is responsible for installing and managing the
  ISC BIND nameserver. It supports DNSSEC, key rollovers, multiple DNS zones,
  views and many more features.

- The :ref:`debops.apparmor` role can be used to manage AppArmor configuration
  and profiles. It will be included in the :file:`layer/common.yml` playbook in
  the future.

- The :ref:`debops.apt_mirror` role can be used to create a mirror of one or
  multiple APT repositories and publish them for other hosts to use as package
  source.

General
'''''''

- DebOps now includes a custom version of the
  ``community.general.apache2_module`` Ansible module, available as
  ``debops.debops.apache2_module``. The custom module includes a fixed
  idempotency check for enabled Apache 2 modules that works on Debian or Ubuntu
  hosts. The :ref:`debops.apache` Ansible role will use this module instead of
  the original one.

- The :command:`debops exec` command can be used to execute Ansible modules
  against hosts in the project directory; this is a wrapper for the
  :command:`ansible` command.

- The :command:`debops run`, :command:`debops check` and :command:`debops exec`
  commands can emit ASCII "bell" at the end of Ansible execution to notify user
  after long runs. Use the ``-E`` or ``--bell`` option to enable this.

- The :command:`debops env` command can be used to inspect the runtime
  environment variables present when other DebOps commands are used, as well as
  execute external commands inside of that runtime environment. This is handy
  for using various :command:`ansible-*` commands within DebOps project
  directories.

- DebOps monorepo now includes configuration for the `pre-commit`__ hook to
  verify changes before they are committed to the repository. Multiple checks
  are performed, notably `codespell`__ is used to find spelling mistakes. More
  checks will be enabled in the future.

  .. __: https://pre-commit.com/
  .. __: https://github.com/codespell-project/codespell

- New project directory layout called "modern" has been implemented in DebOps
  scripts. It can be created using the command:

  .. code-block:: console

     debops project init -t modern <project>

  The modern project layout supports multiple Ansible inventories encapsulated
  into :ref:`infrastructure views <project_infrastructure_views>`.

- DebOps scripts now support management of the project directories using
  :command:`git` as VCS repositories. New project directories will use
  :command:`git` by default. This also enables support for secrets encrypted
  using :command:`git-crypt`.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role now supports management of the "Deb822" format of the APT repository
  sources.

:ref:`debops.avahi` role
''''''''''''''''''''''''

- The role will ensure that the :command:`systemd-resolved` service Multicast
  DNS support is disabled to avoid conflict with the :command:`avahi-daemon`
  service.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- Multicast DNS traffic is accepted by default in the firewall to allow for the
  ``.local`` mDNS domain resolution by the :command:`systemd-resolved` service.
  The role provides a set of variables to limit the traffic by subnet, or
  disable it completely.

:ref:`debops.icinga_web` role
'''''''''''''''''''''''''''''

- The role can now create host and service templates using Icinga Director API.
  This should improve the initial deployment experience, since users don't need
  to create basic host templates by hand before registering hosts in Icinga.

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- The Debian Installer Menu can now install Debian GNU/Linux 12 (Bookworm).

:ref:`debops.java` role
'''''''''''''''''''''''

- The role will now configure the default security policy for Java
  applications. The additions will permit Java applications to access the
  system-wide CA certificate store in :file:`/etc/ssl/certs/` directory as well
  as the PKI infrastructure managed by the :ref:`debops.pki` role, so that Java
  applications can use the existing X.509 certificates and private keys for TLS
  encryption support.

:ref:`debops.keyring` role
''''''''''''''''''''''''''

- The role can now download APT repository GPG keys to separate keyring files,
  which can be used to scope a given GPG key to specific APT repositories.

:ref:`debops.kibana` role
'''''''''''''''''''''''''

- The role can now manage passwords and other confidential data stored in the
  Kibana keystore.

:ref:`debops.mount` role
''''''''''''''''''''''''

- The role can now create custom files which can be used to store credentials
  required to mount remote devices.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- The role will enable LDAP support in NetBox if LDAP environment managed by
  the :ref:`debops.ldap` role is detected on the host. Currently only user
  authentication and Django ACL system is supported via LDAP groups.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The server configuration files can now contain :command:`nginx` configuration
  outside of the ``server`` and ``upstream`` blocks using the new
  ``item.toplevel_options`` parameter.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Support to host the application on a subpath for security reasons.

:ref:`debops.python` role
'''''''''''''''''''''''''

- The :file:`service/python_raw` playbook used during early bootstrap process
  can now inject host entries into the :file:`/etc/hosts` configuration file to
  permit DNS name resolution early during bootstrapping.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- The :ref:`debops.resources` role can now be used to install pip library
  dependencies or virtual environments via the ``ansible.builtin.pip``
  module.

- The :ref:`debops.resources` role can now be used to replace a line via the
  ``ansible.builtin.replace`` module.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The playbook can now be configured to skip the saslauthd role execution.

:ref:`debops.zabbix_agent` role
'''''''''''''''''''''''''''''''

- The role now supports management of Zabbix Agent (written in C) as well as
  Zabbix Agent 2 (written in Go), available in Debian repositories. Only one
  flavor can be managed at a time, but role provides an easy way to switch
  between the two flavors.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.roundcube` role, the Roundcube version installed by
  default has been updated to ``1.6.0``.

- In the :ref:`debops.ipxe` role, the Debian Buster netboot installer version
  has been updated to the next point release, 10.13. Debian Bullseye has been
  updated to the next point release as well, 11.8. The Debian Bookworm release
  has been updated to 12.2.

- In the :ref:`debops.netbox` role, the NetBox version has been updated to
  ``v3.4.2``.

- In the :ref:`debops.owncloud` role, the ownCloud support has been updated to
  ``v10.10``.

- In the :ref:`debops.owncloud` role, the Nextcloud support has been updated to
  ``v24.0`` and ``v25.0``.

General
'''''''

- Tasks which use modules and plugins from the ``ansible.builtin`` Ansible
  Collection have been updated to refer to them via their Fully Qualified
  Collection Names (for example ``ansible.builtin.file`` instead of ``file``).
  This is due to changing requirements of the :command:`ansible-lint` tool.

  New submissions to the DebOps project will be required to use the FQCNs as
  well.

- Various roles that lookup SSH public keys on the Ansible Controller
  (:ref:`debops.preseed`, :ref:`debops.reprepro`, :ref:`debops.system_users`)
  will try to use the :file:`~/.ssh/authorized_keys` file to find the keys if
  all other methods fail.

- In the :file:`site.yml` playbook, the :file:`sys.yml` and :file:`net.yml`
  playbooks will be executed before the :file:`common.yml` playbook. This
  should ensure that configuration of certain resources like mount points or
  LVM pools is present before the system is prepared for general operation.

- The :file:`ansible/playbooks/tools/reboot.yml` Ansible playbook has been
  moved to :file:`ansible/playbooks/reboot.yml` file and uses the new
  :ref:`debops.reboot` Ansible role to perform operations. To use it, you can
  run the ``reboot`` playbook instead of ``tools/reboot``.

- The :file:`ansible/playbooks/tools/upgrade-reboot.yml` Ansible playbook has
  been moved to :file:`ansible/playbooks/upgrade.yml` file and will no longer
  reboot the host automatically. Users can chain the ``upgrade`` and ``reboot``
  playbooks to achieve the previous behaviour, for example:

  .. code-block:: console

     debops run upgrade reboot -l <host>

- The debops-contrib :file:`dropbear_initramfs` playbook has been moved to
  the :ref:`debops.dropbear_initramfs` playbook. The role variable
  ``dropbear_initramfs__host_authorized_keys`` now uses the same keys as
  the ``ansible.posix.authorized_key`` module.

- Various tasks that interact with the MariaDB/MySQL databases will now use the
  :file:`/run/mysqld/mysqld.sock` UNIX socket to do so, due to changes in
  MariaDB restricting local connections for the ``root`` UNIX account.

- The HTML documentation build process has been improved. The
  :command:`yaml2rst` script will be invoked only when a defaults file is
  modified, significantly speeding up documentation rebuilds. Users can also
  modify the :command:`sphinx` options specified in the Makefile via an
  environment variable if they wish.

- The :file:`ansible/playbooks/tools/dist-upgrade.yml` Ansible playbook now has
  MTA configuration exposed via variables in case the mail should be sent via
  a remote server instead of a local one.

- DebOps playbooks have been reorganized to not use a large set of symlinks
  inside of the repository. Instead different sections of the :file:`site.yml`
  playbook have been organized into "layers", new playbooks are located under
  the :file:`ansible/playbooks/layers/` subdirectory. See the new
  :ref:`playbooks` documentation for more details.

- The new :ref:`debops.timesyncd` role has replaced the :ref:`debops.ntp` role
  as the default NTP service provider in the :file:`layer/common.yml` playbook.
  Existing hosts shouldn't be affected - the new role can automatically
  recognize that a different time daemon package is installed on the host and
  will not try to configure :command:`systemd-timesyncd` service in such case.
  You might need to add your hosts to the ``[debops_service_ntp]`` Ansible
  inventory group to keep using the old role.

- The new :ref:`debops.resolved` role has replaced the :ref:`debops.resolvconf`
  role as the default DNS resolver in the :file:`layer/common.yml` and the
  bootstrap playbooks. Existing hosts shouldn't be affected, the role detects
  presence of the ``resolvconf`` APT package and does not modify the host
  configuration in such case.

- Multiple DebOps Collections on Ansible Galaxy have been merged into a single
  ``debops.debops`` Collection to prepare the project to switch role references
  to FQCNs. This is also a test to see if Ansible Galaxy allows >2 MB
  collection tarballs.

- The :command:`debops config` command has been refactored and split into
  multiple subcommands to allow easier configuration introspection. See
  :ref:`it's documentation page <cmd_debops-config>` for more details.

- The Debian 12 (Bookworm) has been released! Multiple DebOps roles have been
  updated and switched the "stable" release to Bookworm, with Bullseye becoming
  the "oldstable" release. The new Debian Testing release, "Trixie" has also
  been added in relevant places.

- DebOps now supports using :command:`git` in project directories - new
  projects will be initialized as :command:`git` repositories by default. The
  :command:`git-crypt` command is also supported, and can encrypt project
  secrets.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role will configure APT to use Debian Security repositories via the
  http://deb.debian.org/debian-security/ CDN.

- The role has been refreshed and management of the
  :file:`/etc/apt/sources.list` file was redesigned to allow for better
  flexibility in configuration. See role documentation for more details.

:ref:`debops.apt_preferences` role
''''''''''''''''''''''''''''''''''

- The pin priorities for the Debian ``-updates`` and ``-security`` APT
  repositories have been raised to 550 to match the raised priority of the
  primary repository. This should ensure that when the custom pin priorities
  are active, updates to Debian packages are correctly installed as well. See
  :envvar:`apt_preferences__debian_stable_default_preset_list` variable for
  details.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- The role can now directly handle the daemon ``log-driver`` parameter.

- The role has been redesigned from scratch; Python :command:`virtualenv`
  support has been removed since the :command:`docker-compose` is included in
  Debian repositories directly, or is implemented as a Go plugin in upstream
  repositories. The Docker configuration is now implemented via the
  :ref:`universal_configuration` system, users will have to modify their
  Ansible inventories. See the role documentation for details.

:ref:`debops.elasticsearch` role
''''''''''''''''''''''''''''''''

- The role will check the status of the built-in user accounts via the HTTP API
  instead of relying on the Ansible local facts and create them if they don't
  exist. This should help with an upgrade of existing Elasticsearch clusters
  without TLS encrypted traffic and authentication.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The role has been rewritten from scratch and now can be used to deploy and
  manage a `GitLab Omnibus`__ instance (managed internally by Chef) on Debian
  or Ubuntu hosts. The role integrates with various DebOps services (firewall,
  PKI infrastructure, LDAP environment) with GitLab Omnibus. Both Community
  Edition (default) and Enterprise Edition are supported.

  .. __: https://docs.gitlab.com/omnibus/

:ref:`debops.global_handlers` role
''''''''''''''''''''''''''''''''''

- The :command:`systemd` handlers have been moved to a separate
  :file:`handlers/systemd.yml` configuration file.

:ref:`debops.icinga` role
'''''''''''''''''''''''''

- New hosts will be added to Icinga Director using the ``icinga-agent-host``
  template, created by default by the :ref:`debops.icinga_web` role. On
  existing installations, you should either create this template by hand, or
  run the :ref:`debops.icinga_web` role so that it gets added automatically.

:ref:`debops.icinga_db` role
''''''''''''''''''''''''''''

- The role will manage Icinga databases directly instead of relying on
  :command:`dbconfig` Debian subsystem. This improves support for remote Icinga
  database deployments accessible over TLS.

:ref:`debops.icinga_web` role
'''''''''''''''''''''''''''''

- The LDAP configuration used by the role to configure LDAP access will be
  based on the :ref:`debops.ldap` Ansible local facts instead of static values,
  to better support modified environments.

:ref:`debops.influxdata` role
'''''''''''''''''''''''''''''

- InfluxData has published a new APT repository GPG key, the role should
  refresh it automatically.

:ref:`debops.minio` role
''''''''''''''''''''''''

- The role has been updated to support newer MinIO features, like the embedded
  MinIO Console. Some of the instance parameters have been changed, for example
  access key and secret key have been replaced with root account and password.
  Check the role documentation for more details.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Configure the :file:`nginx.service` systemd unit to start the
  :command:`nginx` service after the network is configured. This way
  :command:`nginx` should be able to resolve upstream services specified via
  DNS names at startup.

:ref:`debops.ntp` role
''''''''''''''''''''''

- The default NTP daemon used on hosts with the :command:`systemd` service
  manager will be :command:`systemd-timesyncd`. Existing systems with
  a different NTP server should not be affected by this change.

- The role should better detect Linux Container environment and not try to
  install an NTP daemon inside of a container.

:ref:`debops.pki` role
''''''''''''''''''''''

- The :command:`pki-realm` script will call the :command:`certbot` command with
  the :command:`certbot --authenticator <plugin>` option explicitly to allow
  use with third-party authenticator plugins that might not support the
  :command:`certbot --<plugin>` syntax.

:ref:`debops.preseed` role
''''''''''''''''''''''''''

- The default guided partition recipe used by the Debian Installer is changed
  from ``atomic`` to ``multi``. This should allow for easier changes in the
  partition layout via LVM due to separate partitions for :file:`/home` and
  :file:`/var` mount points.

:ref:`debops.proc_hidepid` role
'''''''''''''''''''''''''''''''

- The role will check if PolicyKit is installed on the host, in which case the
  default security level for access to the :file:`/proc` filesystem will be
  more permissive.

:ref:`debops.python` role
'''''''''''''''''''''''''

- The role will enable Python 2.7 support via the fact script only when an
  existing Python 2.7 installation is detected. This change should help avoid
  installing Python 2.7 packages on newer OS releases when they might be
  unavailable.

- The :file:`/etc/pip.conf` configuration file template can be overridden via
  the DebOps template override mechanism.

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- In the :ref:`debops.resolvconf` role, you can now write a fully static
  :file:`/etc/resolv.conf` file without the ``resolvconf`` package.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The default log level used by OpenLDAP has been changed from ``stats`` to
  ``none`` to minimize log output in large environments. This can be modified
  using Ansible inventory in case that the authentication, accounting or search
  metrics are needed.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The management of the :file:`/etc/ssh/sshd_config` configuration file has
  been redesigned and now uses :ref:`universal_configuration`. Multiple default
  variables have been removed as a result. Any changes in configuration applied
  through Ansible inventory might need to be converted to the new format. Check
  the changes on existing hosts before applying new configuration.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- The role will check remote user databases for local admin information using
  the :command:`getent passwd` command if the user has not been found in the
  :file:`/etc/passwd` local database.

Fixed
~~~~~

General
'''''''

- Extrepo facts file did not detect a disabled repository as being disabled
  due to a change in the extrepo file format.

- Ensure that the custom Ansible plugins included in DebOps are present in the
  Ansible Collection build from the DebOps repository.

- Provide a help message in case the :file:`ansible.cfg` configuration file in
  the DebOps project directory does not include the ``inventory`` option.

- Fixed an issue with custom Ansible plugins not working in "standalone" mode
  without the DebOps scripts installed on Ansible Controller.

- The ``warn`` parameter in the ``shell`` and ``command`` Ansible modules has
  been removed in Ansible 2.14. It has been removed in various DebOps roles to
  allow playbook execution to work correctly.

- Fixed all password lookups which used ``chars=ascii`` instead of
  ``chars=ascii_letters``. This resulted in passwords which only contained the
  letters a,c,i,s instead of all lowercase and uppercase ASCII letters. Because
  all occurrences of this bug at least also included all digits in the character
  set and the password length was at least 20 characters, this did not result
  in weak passwords.

- The ``ipaddr`` Ansible filter and its aliases used in various roles were
  renamed to ``ansible.utils.ipaddr`` and its corresponding alias names because
  Ansible requires use of FQCNs in filters. The ``ansible.utils`` Ansible
  Collection is now a dependency of the DebOps Collection.

- The :command:`debops run` and :command:`debops check` commands should now
  correctly recognize options of the :command:`ansible-playbook` command which
  don't expect arguments and expand playbook names specified after them.

:ref:`debops.apt` role
''''''''''''''''''''''

- In the fact script, parse the ``deb-src`` configuration entries before
  ``deb`` entries to ensure that there are no duplicates.

- The role no longer defaults to the ``ansible_local.core.distribution`` and
  ``ansible_local.core.distribution_release`` local facts for determining the
  Linux distribution and the distribution release, respectively. These facts
  were set later in the common playbook, meaning that the role would restore
  the previous distribution release in ``/etc/apt/sources.list`` after a
  distribution upgrade.

debops.boxbackup role
'''''''''''''''''''''

- The role is not included in the DebOps Collection on Ansible Galaxy,
  therefore its playbook is no longer included in the main :file:`site.yml`
  playbook. This fixes an issue with Ansible stopping the site playbook
  execution when it cannot find the ``boxbackup`` role in the Collection.

:ref:`debops.core` role
'''''''''''''''''''''''

- Ensure that the ``ansible_controllers`` fact can be reset using the
  :envvar:`core__remove_facts` variable to avoid infinitely growing list of
  Ansible Controllers.

:ref:`debops.cron` role
'''''''''''''''''''''''

- Fixed the order of job parameters applied by the role - now parameters from
  a specific job will override parameters specified for all jobs in a given
  configuration entry.

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- Fixed service configuration mistake when DHCPv6 mode is set to an empty
  string. The configuration template should take this into account and add
  a correct separator (or omit it) in the generated configuration file.

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- The role's PKI hook script still referenced an old configuration file that
  was no longer being managed by :ref:`debops.dovecot` since the role redesign,
  resulting in the hook script failing to reload dovecot after a certificate or
  DH param change.

:ref:`debops.elasticsearch` role
''''''''''''''''''''''''''''''''

- The internal Java security policy used by Elasticsearch will be configured
  only on Elasticsearch v7.x+ versions. Before them, Elasticsearch used the
  global Java security policy.

:ref:`debops.environment` role
''''''''''''''''''''''''''''''

- Fixed issues with preserving environment variables across multiple role
  executions.

:ref:`debops.etc_aliases` role
''''''''''''''''''''''''''''''

- Don't save dependent recipients on Ansible Controller if they are not
  defined. This should avoid creating unnecessary files in AWX job containers.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- Don't include additional '{' or '}' characters in certain rules when the
  ``domain_args`` parameter is specified.

- Fixed an issue in the rule template that caused a templating type error where
  Jinja expected a string but found an int value instead.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- Fixed an error that could occur in the "Patch 'vagrant-libvirt' source code"
  task on systems other than Debian 9 or 10. The patch is not required since
  the ``vagrant-libvirt`` v0.1.0 package.

:ref:`debops.grub` role
'''''''''''''''''''''''

- The :command:`grub` user passwords will be passed for encryption using
  a temporary file stored in the :file:`secret/` directory on the Ansible
  Controller instead of directly on the command line, to avoid leaks through
  the process list.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- The interface names used in scripts will be escaped using the
  :command:`systemd-escape` tool. This should fix problems with control over
  network interfaces which contain the hyphen character(s).

:ref:`debops.kibana` role
'''''''''''''''''''''''''

- The role will use the correct path of the Kibana keystore depending on the
  installed version (versions <7.0.0 keep the keystore in the
  :file:`/var/lib/kibana/` directory; newer versions use the
  :file:`/etc/kibana/` directory).

- The role will use different user account depending on Kibana version (either
  ``kibana``, or ``kibana_system`` used in newer installations of
  Elasticsearch). Depending on your installed version, you should check the
  :envvar:`kibana__elasticsearch_username` to verify that the correct account
  is used for access to Elasticsearch.

- The role will include the ``server.publicBaseUrl`` parameter depending on
  Kibana version, to avoid failures on older Kibana installations.

:ref:`debops.ldap` role
'''''''''''''''''''''''

- Fixed an issue with the role passing IP and MAC addresses to the LDAP
  directory as a nested YAML list which resulted in a wrong attribute values.

- Fixed an issue with role parsing the already parsed Ansible facts to extract
  IP/CIDR information which resulted in wrong output in certain cases. The role
  will now implicitly trust the Ansible facts to be correct when adding IP and
  prefix details to the LDAP database.

:ref:`debops.libvirtd` role
'''''''''''''''''''''''''''

- Fixed ``qemu-kvm`` package installation logic; the KVM packages should now be
  handled correctly on Debian Bullseye and newer releases.

:ref:`debops.logrotate` role
''''''''''''''''''''''''''''

- Fixed formatting in the :file:`/etc/logrotate.conf` configuration file to
  avoid adding :command:`vim` fold markers from the DebOps role defaults.

:ref:`debops.lxc` role
''''''''''''''''''''''

- Fixed name of the ``vfs_root`` parameter in the call to the
  ``community.general.lxc_container`` Ansible module, which was renamed to
  ``zfs_root``.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- In the fact script, don't use ``in`` for matching IP addresses and DNS names
  where substring matching is undesirable.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- Using boolean variables in :envvar:`netbox__config_plugins_config` for
  example resulted in an error because the role used the ``to_nice_json``
  Jinja2 filter internally to render Python configuration.
  This is fixed for all uses of ``to_nice_json``

:ref:`debops.ntp` role
''''''''''''''''''''''

- Fix an issue where the role tried to manage the :command:`systemd-timesyncd`
  service without it actually being present on the host. This should now be
  avoided by carefully checking the service status.

- The role will not try to purge installed NTP daemon packages when it is
  disabled through Ansible inventory.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Access to static assets was not logged regardless of the
  ``owncloud__nginx_access_log_assets`` setting.

- Access to the ``/remote`` URI path was not configured in Nginx as proposed in
  the upstream Nginx example in the Nextcloud docs.

:ref:`debops.pdns` role
'''''''''''''''''''''''

- On pdns installations with version >= 4.5.0 (e.g. on Bookworm systems), the
  role would cause a syntax error on the local-address configuration option.

:ref:`debops.pki` role
''''''''''''''''''''''

- After the :command:`certbot` script performs a certificate renewal operation,
  a deploy hook will update the PEM chains in a given PKI realm
  :file:`private/` directory to include the new private key created by the
  :command:`certbot` script.

- Fixed an issue where when a PKI realm was initialized for ACME/Let's Encrypt
  support, second level domains were not included in the generated X.509
  certificate request.

- Use :command:`openssl x509 -inform PEM` command to explicitly check for
  a PEM-formatted X.509 certificate file because the old :command:`openssl x509
  -in` option was changed to work with both DER and PEM files. This should fix
  an issue with Let's Encrypt certificate chains containing a DER-formatted
  certificate inside of them.

  Users will need to remove existing PKI realms which use ACME/Let's Encrypt CA
  for the :command:`pki-realm` script to rebuild the certificate chain
  correctly. After that re-run the :ref:`debops.pki` role on the host to
  re-create che realms.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- The EHLO IP address check was removed. This check would reject a message if
  the EHLO hostname of the connecting mailserver resolved to a non-publicly
  routable IP address. However, rejecting messages for this reason is
  prohibited by :rfc:`5321` section 4.1.4, and sometimes caused deliverability
  issues for Office 365 users.

:ref:`debops.preseed` role
''''''''''''''''''''''''''

- Fixed an issue with the ``d-i`` keyboard preseed that resulted in the
  ``keyboard-configuration`` APT package not being installed and configured
  correctly. The default keymap is changed to ``us`` and the option is no
  longer based on the system language which might be incorrect in this case.

:ref:`debops.proc_hidepid` role
'''''''''''''''''''''''''''''''

- The fact script has been optimized for environments with large UNIX group
  databases, for example connected to ActiveDirectory domains.

:ref:`debops.prosody` role
''''''''''''''''''''''''''

- The ``prosdoy__pki_realm_path`` variable has been renamed to
  :envvar:`prosody__pki_realm_path` to fix the typo in the variable name. You
  might need to update your inventory in this case so that the role gets
  correct value.

:ref:`debops.python` role
'''''''''''''''''''''''''

- In the fact script, correctly parse the subprocess output to find out the
  version of installed Python executables.

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- Fixed an issue where the custom hook script did not add static
  :command:`resolvconf` configuration after host was rebooted, when the
  :file:`/run/resolvconf/` path did not exist. It will be created automatically
  if not found.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- Locked ``johndoh/contextmenu`` plugin to version 3.2.1 for Roundcube < 1.5
  due to compatibility issues.

:ref:`debops.secret` role
'''''''''''''''''''''''''

- Fixed an issue with the :envvar:`secret` variable not being defined in other
  roles in newer Ansible versions.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The role will now correctly handle hosts where :command:`sshd` is launched
  via :command:`systemd` socket activation mechanism.

:ref:`debops.sudo` role
'''''''''''''''''''''''

- The fact script will check :command:`sudo` version using the :command:`dpkg`
  command to avoid running :command:`sudo` on each Ansible fact gathering. This
  proved problematic when LDAP support is enabled and the LDAP directory is not
  available for any reason - :command:`sudo` tries to connect to the directory
  and times out, slowing Ansible run into a crawl.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- Fixed an issue in the configuration template that caused a templating type
  error where Jinja expected a string but found an int value instead.

- The :file:`protect-links.conf` configuration file has been renamed to
  :file:`99-protect-links.conf` file in Debian Bookworm; this is handled
  conditionally in the role configuration. Users might need to remove the
  :file:`/etc/sysctl.d/protect-links.conf` file generated by the role manually
  on existing installations to fix this issue.

Removed
~~~~~~~

General
'''''''

- Support for end-of-life Debian and Ubuntu releases has been removed from
  Ansible roles included in the DebOps project. The releases dropped are:
  "Debian Wheezy", "Debian Jessie", "Ubuntu Precise Pangolin". The support is
  still available in stable DebOps releases up to v3.0.x if needed.

- Federated Learning of Cohorts opt-out in the :ref:`debops.apache` and
  :ref:`debops.nginx` roles has been removed. Google `abandoned the feature`__
  in favor of Topics API in web browsers.

  .. __: https://blog.google/products/chrome/get-know-new-topics-api-privacy-sandbox/

- The :command:`debops project status` subcommand has been removed. Its
  functionality is now incorporated within the DebOps configuration tree
  accessible using the :ref:`cmd_debops-config` command.

- The :command:`debops-api` code and Ansible role has been removed from the
  project, since it's not relevant anymore after separate :command:`git`
  repositories were merged into a monorepo.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The ``ranger`` APT package will not be installed by default. The ``mc``
  package can be used as an alternative. Or you can consider installing
  ``nnn``.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Drop ownCloud full auto upgrade support. Was never fully supported. Strategy
  of Nextcloud is Docker to provide auto upgrades. DebOps will not provide a
  custom solution.


`debops v3.0.0`_ - 2022-02-17
-----------------------------

.. _debops v3.0.0: https://github.com/debops/debops/compare/v2.3.0...v3.0.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.minidlna` role configures the MiniDLNA service that can be
  used to provide media (video, music, images) to other devices on the local
  network that support the DLNA protocol.

- The :ref:`debops.pdns` role manages the `PowerDNS Authoritative Server`__,
  which is an authoritative DNS server with support for DNSSEC, DNS UPDATE,
  geographical load balancing, and storing zone data and metadata in one or
  more backends like relational databases, LDAP databases, and plain text
  files.

  .. __: https://www.powerdns.com/auth.html

- The :ref:`debops.telegraf` role can be used to install and manage the
  `Telegraf`__ metrics server, which can send data to various other services.

  .. __: https://www.influxdata.com/time-series-platform/telegraf/

- The :ref:`debops.lldpd` role provides support for managing and configuring
  the :command:`lldpd` service, which can be used to locate other network
  devices connected to a given host using the Link-Layer Discovery Protocol.
  The role is included in the :file:`common.yml` playbook by default.

- The :ref:`debops.zabbix_agent` role can install and configure Zabbix Agent,
  used for monitoring and metrics.

- The :ref:`debops.keepalived` role can be used to install and manage
  :command:`keepalived` daemon, a lightweight load balancing and high
  availability service.

- The :ref:`debops.rspamd` role can be used to install `rspamd`__ service, an
  anti-spam mail filter. The role automatically integrates with the
  :ref:`debops.postfix` role to provide anti-spam support.

  .. __: https://rspamd.org/

- The :ref:`debops.imapproxy` role can install and configure the IMAP Proxy
  service, useful for web mail applications that use IMAP to access the mail
  services.

General
'''''''

- New Jinja filters ``from_toml`` and ``to_toml`` are available to DebOps
  roles, provided using a custom Ansible plugin. The filters require the
  ``toml`` Python package to be installed on the Ansible Controller.

- New Ansible custom lookup plugin ``dig_srv`` can be used in Ansible variables
  and tasks to simplify DNS SRV record parsing. The plugin can retrieve an
  existing SRV record or if none is found, fall back to a predefined default
  values for the hostname and port.

- A new Ansible tag, ``meta::facts`` has been added in all DebOps roles to the
  tasks that install Ansible local facts. This can be useful during initial
  provisioning to avoid issues with Ansible ``--check`` mode when certain
  configurations depend on the presence of the local facts to gather details
  from the remote hosts.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role can now enable additional Debian architectures on a given host,
  which allows for `Multiarch`__ installations.

  .. __: https://wiki.debian.org/Multiarch/HOWTO

- You can now purge specific APT packages along with their configuration and
  unused dependencies. This might be useful during bootstrap or provisioning
  process to remove unused or conflicting services installed by the provider.

- The role can now configure :file:`/etc/apt/auth.conf.d/` configuration files
  to enable access to restricted APT repositories that require HTTP Basic
  Authentication.

:ref:`debops.dokuwiki` role
'''''''''''''''''''''''''''

- The role now provides a set of variables and tasks which can be used to add
  or remove custom files in the DokuWiki installation, useful in certain
  setups.

:ref:`debops.elasticsearch` role
''''''''''''''''''''''''''''''''

- In a cluster deployment on hosts with PKI environment configured, the role
  will automatically enable the X-Pack plugin and configure TLS encryption for
  HTTP client and inter-cluster communication.

- Elasticsearch user accounts and role definitions can be managed via Ansible
  using the API access, when the encrypted communication and X-Pack plugin is
  enabled. The role will initialize a set of built-in user accounts in the
  Elasticsearch cluster automatically.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The ``arptables`` and ``ebtables`` APT packages will be installed by default.
  This is needed so that various alternatives for :command:`iptables` backends
  can be correctly synchronized.

:ref:`debops.keyring` role
''''''''''''''''''''''''''

- The role can now configure :file:`/etc/apt/auth.conf.d/` configuration files
  to enable access to restricted APT repositories that require HTTP Basic
  Authentication.

:ref:`debops.kibana` role
'''''''''''''''''''''''''

- If the username and password for connection to the Elasticsearch service are
  provided, the role will configure Kibana to use TLS encryption for
  communication with the Elasticsearch cluster, based on the PKI environment
  managed by the :ref:`debops.pki` Ansible role.

:ref:`debops.libvirtd` role
'''''''''''''''''''''''''''

- The role will now install UEFI firmware for amd64 VMs, alongside traditional
  BIOS.

:ref:`debops.lvm` role
''''''''''''''''''''''

- The role can now manage `LVM Thin Pool Logical Volumes`__.

  .. __: https://man7.org/linux/man-pages/man7/lvmthin.7.html

- It is now possible to apply custom options to :ref:`lvm__thin_pools` and
  :ref:`lvm__logical_volumes`.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role can define a list of SSH identities added to the ``root`` UNIX
  account in new LXC containers by default. This can be used to grant multiple
  system administrators access to the containers.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- The :man:`hosts(5)` database FQDN entries defined as strings will
  automatically create hostname aliases when the role uses a template to
  generate the :file:`/etc/hosts` database.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role can be used in "config-only" mode where the :command:`nginx`
  packages are not installed but are expected to be present and in
  configuration compatible with DebOps.

- The :command:`nginx` server can now be configured to send logs to the
  :command:`syslog` service via a :file:`/dev/log` UNIX socket, instead of
  storing them in separate configuration files.

:ref:`debops.pki` role
''''''''''''''''''''''

- The role gained support for `Certbot`__ tool as an alternative to
  :command:`acme-tiny` script. Certbot provides `Lets' Encrypt DNS-01
  challenge`__ functionality with wildcard and internal certificates. See role
  documentation for more details.

  .. __: https://certbot.eff.org/
  .. __: https://letsencrypt.org/docs/challenge-types/#dns-01-challenge

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- It is now possible to override the default ``netstream_driver``,
  ``driver_mode`` and ``driver_authmode`` parameters in every
  :ref:`rsyslog__ref_forward` forwarding rule.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The ``sshd__ferm_interface`` variable can now be used to limit access to SSH
  via the host firewall based on interface.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The `SCHema for ACademia`__ (schac) LDAP schema has been added to the role to
  provide more LDAP attributes and object classes useful in university
  environments.

  .. __: https://wiki.refeds.org/display/STAN/SCHAC

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The ``systemd`` Debian package in Debian Bullseye provides
  a :command:`sysctl` configuration file which increases the maximum number of
  PIDs allowed by the kernel. The role will create a "masked" configuration
  file to ensure that :command:`sysctl` configuration works in LXC containers,
  where the ``kernel.pid_max`` parameter will be commented out since it cannot
  be modified from inside of a container. On hardware and VM hosts the
  configuration will be applied as expected.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Buster netboot installer version
  has been updated to the next point release, 10.11. Debian Bullseye has been
  updated to the next point release as well, 11.2.

  Debian 11 (Bullseye) has been released. The :ref:`debops.ipxe` role will now
  prepare a netboot installer with this release and set Bullseye as the default
  Stable installation option.

- The :file:`lxc_ssh.py` Ansible connection plugin has been updated to include
  latest changes and bugfixes.

- The Elastic APT repository configured on new installations by
  :ref:`debops.elastic_co` has been updated to version 7.x. Updating the
  repository configuration on existing hosts requires that you manually update
  the local facts or to set the ``elastic_co__version`` variable to '7.x' before
  running the playbook.

- In the :ref:`debops.netbox` role, the NetBox version has been updated to
  ``v3.1.6``. Note that you need ``v2.11.0`` or later to upgrade to ``v3.0``.

- The Icinga Web 2 modules installed by :ref:`debops.icinga_web` have been
  updated to their latest versions. A quick database migration is needed after
  updating to get Director to work again. Just click the database migration
  button on the 'Icinga Director' -> 'Activities log' page.

- In the :ref:`debops.roundcube` role, the Roundcube version installed by
  default has been updated to ``1.4.13``.

- Drop Nextcloud 20 and 21 support because they are EOL. You need to upgrade
  Nextcloud manually if you are running version 21 or below. The role now
  defaults to Nextcloud 22 for new installations.

- In the :ref:`debops.wpcli` role, the WpCli version has been updated to
  ``2.5.0``. ``2.3.0`` and ``2.4.0`` can be installed by changing ``wpcli__version``

General
'''''''

- DebOps tasks that import local SSH keys will now recognize FIDO U2F security
  keys used via the SSH agent.

- The APT configuration by the :ref:`debops.apt` and :ref:`debops.apt_proxy`
  roles in the :file:`common.yml` playbook has been moved to a separate play to
  ensure feature parity with the bootstrap playbooks.

- The :command:`debops` Python scripts have been completely rewritten and
  reorganized. The UI has been redesigned to use subcommands rather than
  separate scripts. This pans the way for easy extension of the script
  functionality in the future and improvements for various tasks done on the
  Ansible Controller.

- The DebOps monorepo can now be used as an "Ansible Collection" when path to
  the :file:`ansible/collections/` subdirectory inside of the :command:`git`
  repository is specified in the `collections_paths`__ variable in the Ansible
  configuration file.

  .. note:: The roles and plugins included in DebOps are not yet fully
            compatible with the Collection system. They will be converted at
            a later time.

  .. __: https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths

- The base Docker image used by DebOps Dockerfile has been changed from
  ``debian:buster-slim`` to ``debian:bullseye-slim``. The Dockerfile has been
  updated to build and install DebOps from the monorepo instead of installing
  a release from PyPI.

- The references for custom Ansible lookup and filter plugins have been
  modified to use the Fully Qualified Collection Name format to allow the
  DebOps monorepo to work as an Ansible Collection.

- Custom Ansible plugins included in the :ref:`debops.ansible_plugins` role
  have been copied to the :file:`ansible/plugins/` subdirectories to make them
  available through the Ansible Collection mechanisms.

- Multiple roles that use the DNS ``SRV`` Resource Records to find related
  services have been updated to utilize the new ``dig_srv`` Ansible lookup
  plugin to find the records. This change should make the role code easier to
  maintain.

- Most of the DebOps roles now use :envvar:`debops__no_log` variable in tasks
  with the ``no_log`` Ansible keyword. This should provide an easier way to
  debug issues with various roles.

- Roles which use the :command:`dpkg-divert` Debian utility to preserve
  original configuration files have been updated to use the ``dpkg_divert``
  custom Ansible module included in the DebOps Collection instead of using the
  ``command`` or ``shell`` Ansible modules to manage the diversion and
  reversion.

Continuous Integration
''''''''''''''''''''''

- The default box used by Vagrant for DebOps VMs has been updated from
  ``debian/buster64`` to ``debian/bullseye64``.

LDAP
''''

- The :file:`ldap/init-directory.yml` playbook can now store the administrator
  credentials in the :file:`secret/` directory managed by the
  :ref:`debops.secret` role. THe credentials can also be randomly generated if
  the playbook is used non-interactively.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role defaults have been updated, Bullseye is the new Stable.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The ``haveged`` Debian package will not be installed in a virtual machine if
  the underlying hypervisor technology already provides access to the host's
  RNG device through virtualization.

:ref:`debops.dhparam` role
''''''''''''''''''''''''''

- The role will no longer install the :command:`cron` service directly; instead
  it depends on the :ref:`debops.cron` role to ensure that the service is
  present. This allows replacing the ``cron`` Debian package with a different
  backend, for example ``systemd-cron`` package.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- The role now enables `live restore`__ by default.

  .. __: https://docs.docker.com/config/containers/live-restore/

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- The role has been thoroughly refreshed and now uses the
  :ref:`universal_configuration` format for the service configuration. All role
  variables have been renamed to put them in a separate namespace.

  .. warning:: If you use a Dovecot installation in your environment, you
     should check the new role documentation and update the relevant configuration
     in the Ansible inventory before applying the new role on your infrastructure.

:ref:`debops.elasticsearch` role
''''''''''''''''''''''''''''''''

- The main configuration is reorganized, original contents of the configuration
  file are set in the :envvar:`elasticsearch__original_configuration` variable
  and the options changed by the role are set in the
  :envvar:`elasticsearch__default_configuration` variable.

:ref:`debops.etckeeper` role
''''''''''''''''''''''''''''

- Add ``etckeeper__gitattributes`` option to be able to appended to the
  :file:`/etc/.gitattributes` file.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The backend configuration will now manage all relevant alternatives for
  :command:`arptables`, :command:`ebtables`, :command:`iptables` and
  :command:`ip6tables` commands to keep various parts of the firewall
  synchronized.

  .. warning:: The variable which controls what backend is used has been
               renamed to :envvar:`ferm__iptables_backend_type` due to value
               change. You might need to update your Ansible inventory to select
               the correct backend.

- The default backend for :command:`iptables` is changed to ``legacy`` on newer
  OS releases, because `there's no plans`__ to support :command:`nftables`
  backend by the :command:`ferm` project. You might want to check if the
  firewall configuration is correctly applied after running the role against
  already configured hosts.

  .. __: https://github.com/MaxKellermann/ferm/issues/47

:ref:`debops.grub` role
'''''''''''''''''''''''

- The role now enables the serial console by default.

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- You can now define what kernel parameters are used by default in the Debian
  Installer, using an iPXE variable.

:ref:`debops.keyring` role
''''''''''''''''''''''''''

- The default keyserver used by the role has been changed to `Ubuntu
  keyserver`__ due to deprecation of the SKS Keyserver pool.

  .. __: https://keyserver.ubuntu.com/

:ref:`debops.logrotate` role
''''''''''''''''''''''''''''

- The role will no longer install the :command:`cron` service directly; instead
  it depends on the :ref:`debops.cron` role to ensure that the service is
  present. This allows replacing the ``cron`` Debian package with a different
  backend, for example ``systemd-cron`` package.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- Add ``netbox__config_custom`` option to be able to configure not explicitly
  supported options in a raw format.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The ``item.location_list`` entries in the server configuration can now define
  access policy for a specific location and use subnet ranges or password
  authentication to control access.

- Length and characters included in the passwords generated by the role for
  HTTP Basic Authentication can now be controlled using default variables.

:ref:`debops.php` role
''''''''''''''''''''''

- php7.4 has been added to the ``php__version_preference`` list. This ensures
  that PHP-related packages are installed on Debian 11 (Bullseye) systems.

:ref:`debops.pki` role
''''''''''''''''''''''

- The RootCA certificate for the Let's Encrypt ACME certificates has been
  changed to :file:`mozilla/ISRG_Root_X1.crt`, the previous CA certificate is
  now expired. Existing PKI realms will not be modified, you might need to
  recreate them or replace the :file:`acme/root.pem` symlink manually.

:ref:`debops.postldap` role
'''''''''''''''''''''''''''

- A few changes to the Postfix LDAP lookup tables were made, most notably a
  better split between alias lookups (ldap_virtual_alias_maps.cf) and
  distribution list lookups (ldap_virtual_forward_maps.cf).

:ref:`debops.preseed` role
''''''''''''''''''''''''''

- The role has been redesigned from the ground up and uses
  :ref:`universal_configuration` to manage Preseed configuration files.
  Multiple "flavors" are provided to permit installation of Debian in a variety
  of environments. See the :ref:`upgrade_notes` for details about upgrading an
  existing installation.

:ref:`debops.reprepro` role
'''''''''''''''''''''''''''

- The role has been redesigned from scratch. It can now manage multiple APT
  repository instances on separate DNS domains, repositories can have access
  restrictions, the :command:`inoticoming` service has been replaced by
  a :command:`systemd` ``.path`` units. Repositories are now configured via the
  :ref:`universal_configuration` system. See the new role documentation for
  details.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- The default NetStream driver mode and authentication mode are now set based
  on whether the ``gtls`` driver is enabled.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The :file:`mailservice.schema` LDAP schema has been modified to add new LDAP
  attributes, ``mailPrivateAddress`` and ``mailContactAddress``. This change
  includes additional constraints on uniqueness and requires a rebuild of the
  OpenLDAP service. See :ref:`upgrade_notes` for details.

- The ``sudoUser`` attribute index in the OpenLDAP service has been changed to
  ``sudoHost,sudoUser eq,sub`` to provide better search performance for the
  :command:`sssd` service. This will have to be changed manually on existing
  OpenLDAP installations before the role is idempotent.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- Keep the ``SSH_CONNECTION`` environment variable when running commands with
  sudo.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The role will configure protection for FIFOs and regular files along with
  protection for symlinks and hardlinks, introduced in Debian Bullseye.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- The role assumes that Ansible Controller has Python 3 available and will not
  check for Python 2.7 anymore while gathering local UNIX account details, to
  avoid issues with non-existent host facts.

:ref:`debops.unattended_upgrades` role
''''''''''''''''''''''''''''''''''''''

- The role now defaults to the admin_private_email Ansible fact (as provided by
  :ref:`debops.core`) for the :envvar:`unattended_upgrades__mail_to` variable.

Fixed
~~~~~

General
'''''''

- Fixed an issue with user and group management roles where the UNIX account
  home directories were created even if they were specifically disabled. Roles
  should now be more careful and respect the administrator wishes.

LDAP
''''

- The :file:`ldap/init-directory.yml` playbook should now work better with
  non-local UNIX accounts and provide better defaults for standardized account
  names like ``ansible``.

- The ``*__ldap_bindpw`` variables in various roles have been modified to
  create the passwords only when LDAP support is enabled. This should fix an
  issue in non-LDAP environments where Ansible would stop playbook execution
  when a single password file for an LDAP object was created by multiple hosts,
  generating a race condition due to empty domain part of the Distinguished
  Name.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role no longer disables the backports repository of a Debian LTS or
  archive release.

:ref:`debops.apt_cacher_ng` role
''''''''''''''''''''''''''''''''

- The role no longer creates an unnecessary NGINX webroot directory.

:ref:`debops.dhcpd` role
''''''''''''''''''''''''

- host-identifier parameters are now always quoted in dhcpd6.conf. This is
  needed when the host-identifier contains periods (e.g. fully qualified
  domain names).

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- Ensure that the configuration entries with ``a`` or ``aaaa`` parameter are
  correctly recognized as host entries.

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- Make sure that the correct Preseed flavor is used when the user changes it
  using the menu item.

:ref:`debops.kmod` role
'''''''''''''''''''''''

- Fixed an issue with role facts where the script ended with exception when the
  ``kmod`` package wasn't installed and the :command:`lsmod` command was not
  available.

:ref:`debops.ldap` role
'''''''''''''''''''''''

- The role will refresh the local facts when the :file:`/etc/ldap/ldap.conf`
  configuration changes to ensure that other roles have correct information
  available, for example when a new set of LDAP servers is used.

:ref:`debops.libvirt` role
''''''''''''''''''''''''''

- The ``virt-top`` APT package is not part of the Debian Bullseye release,
  therefore the role will not try to install it by default.

:ref:`debops.libvirtd` role
'''''''''''''''''''''''''''

- The ``virt-top`` APT package is not part of the Debian Bullseye release,
  therefore the role will not try to install it by default.

- The root account will no longer be added to the 'libvirt' group by default.

:ref:`debops.lxc` role
''''''''''''''''''''''

- Use the Ubuntu GPG keyserver by default to download LXC container signing
  keys when the container is created by the :command:`lxc-new-unprivileged`
  script as well as through the ``lxc_container`` Ansible module (the SKS
  keyserver pool has been deprecated).

- Enable AppArmor nesting configuration in LXC v4.0.x version, used in Debian
  Bullseye. Without this, various :command:`systemd` services inside of the
  LXC containers cannot start and SSH/console login is delayed ~25 seconds.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- Fixed an issue where the fact script broke when it tried to find the host's
  IP address using DNS and the host does not have an entry in the DNS or in
  :file:`/etc/hosts` database.

- Fixed an issue where the initial bootstrap and common playbook execution
  didn't provide the correct configuration for the :ref:`debops.netbase` role,
  resulting in a non-idempotent execution and wrong :file:`/etc/hosts` database
  contents. The order of the :ref:`debops.python` role in bootstrap and common
  playbooks has been adjusted to ensure that the Python packages required by
  the :ref:`debops.netbase` role are installed before its execution.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- Set ``client_max_body_size`` to ``25m`` in Nginx as in the NetBox Nginx
  config example.
  Before, it was at the Nginx default of ``1m`` which caused Nginx to reject
  larger picture uploads to NetBox.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Access to the ACME challenge directories is now always allowed, even if a
  server-wide allowlist configuration or HTTP basic authentication enforcement
  has been applied. This ensures that it is always possible to request and renew
  certificates through the ACME protocol.

- Do not remove the whole PKI hook directory when the :command:`nginx` hook
  script is removed by the role.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Fixed an issue with the :ref:`debops.nginx` configuration where some
  Nextcloud pages (LDAP configuration, for example) did not work correctly.

:ref:`debops.pki` role
''''''''''''''''''''''

- Ensure that the X.509 certificate requests generated by the
  :command:`pki-realm` script to renew Let's Encrypt/ACME certificates include
  SubjectAltNames defined in the PKI realm.

:ref:`debops.postfix` role
''''''''''''''''''''''''''

- Do not remove the whole PKI hook directory when the :command:`postfix` hook
  script is removed by the role.

:ref:`debops.proc_hidepid` role
'''''''''''''''''''''''''''''''

- Add the ``procadmins`` UNIX group as a supplementary group in the
  :file:`user@.service` :command:`systemd` unit to fix an issue where the user
  service does not start when unified cgroupv2 hierarchy is used.

:ref:`debops.prosody` role
''''''''''''''''''''''''''

- Do not remove the whole PKI hook directory when the :command:`prosody` hook
  script is removed by the role.

:ref:`debops.rabbitmq_server` role
''''''''''''''''''''''''''''''''''

- Correctly interpret the list of RabbitMQ user accounts to not create unwanted
  vhosts.

:ref:`debops.redis_server` role
'''''''''''''''''''''''''''''''

- Fixed an issue with facts not showing Redis instances correctly when password
  is empty.

debops.reprepro role
''''''''''''''''''''

- Added missing architectures (all expected architectures for Bookworm, and
  some missing architectures for older releases).

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- Ensure that the fact script correctly includes information about upstream
  nameservers when :command:`systemd-resolved` service is used.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- The rsyslog role always configured the streamDriverPermittedPeers option,
  even when the ``anon`` network driver authentication mode was selected.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The role will no longer create an LDAP account when it is not needed.

- The default ``sshd__login_grace_time`` has been increased from 30 to 60
  seconds. This mitigates a lock-out issue when ``sshd__use_dns`` is
  enabled (the default) and your DNS resolvers are unreachable.

- The role will avoid leaking the LDAP bind password through the process list
  during password file creation on the remote host.

:ref:`debops.sudo` role
'''''''''''''''''''''''

- Fixed an issue in the fact script which resulted in a wrong string being
  picked up as the version number when :command:`sudo` was configured to use
  LDAP, but the LDAP service was not available.

- The role will now skip installing the ``sudo-ldap`` package and creating the
  LDAP account object if :envvar:`sudo__ldap_enabled` is ``False``.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The role's default of explicitly disabling packet forwarding conflicted with
  the sysctl configuration done by Docker Server. The role would disable
  essential (for Docker) packet forwarding, which would only be enabled again
  when the Docker daemon was manually restarted or the sysctl parameter was
  manually corrected. This has been fixed by letting the role default to
  enabling packet forwarding on Docker Server hosts.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- The ``create_home`` parameter was not functional because of typos in the
  Ansible task.

Removed
~~~~~~~

General
'''''''

- The old DebOps scripts have been removed from the monorepo, they are replaced
  with new, cleaner scripts that support subcommands.

- The :command:`debops-update` script has been dropped from the project.
  Existing users should use :command:`git clone` command to install the DebOps
  monorepo if they wish to use the rolling release. There's also no need to
  install the ``debops`` PyPI package; DebOps scripts can be installed directly
  from the monorepo in development mode if desired.

- The :command:`debops-task` script has been dropped. You can use the
  :command:`ansible` command directly to perform ad-hoc commands against the
  Ansible inventory.

- The :command:`debops-defaults` script has been removed from the project.
  Easy access to the role defaults will be implemented at a later date.

- The :command:`debops-init` script has been replaced with the :command:`debops
  project init` subcommand.

- The :command:`debops-padlock` script has been removed from the project. It's
  functionality is now available via the :command:`debops project` subcommands.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The support for `SPDY`__ protocol has been removed from the role; it has been
  replaced in the technology stack by `HTTP/2`__ specification.

  .. __: https://en.wikipedia.org/wiki/SPDY
  .. __: https://en.wikipedia.org/wiki/HTTP/2

:ref:`debops.preseed` role
''''''''''''''''''''''''''

- Support for installing and configuring Salt Minions during host provisioning
  has been removed.

:ref:`debops.snmpd` role
''''''''''''''''''''''''

- The tasks and other code which managed the :command:`lldpd` daemon has been
  removed from the role. The :ref:`debops.lldpd` role now provides the LLDP
  support and automatically integrates with SNMP daemon when it is detected.

Security
~~~~~~~~

General
'''''''

- Specific DebOps roles (:ref:`debops.dovecot`, :ref:`debops.owncloud`,
  :ref:`debops.postldap`) used password generation lookups with invalid
  parameters which might have resulted in a weaker passwords generated during
  their deployment. The parameters in the password lookups have been fixed; you
  might consider regenerating the passwords created by them by removing
  existing ones from the :ref:`debops.secret` storage on the Ansible Controller
  and re-running the roles.


`debops v2.3.0`_ - 2021-06-04
-----------------------------

.. _debops v2.3.0: https://github.com/debops/debops/compare/v2.2.0...v2.3.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.extrepo` role provides an interface for the `extrepo`__
  Debian package, an external APT source manager. It can be used to configure
  third-party APT repositories.

  .. __: https://grep.be/blog/en/computer/debian/Announcing_extrepo/

- The :ref:`debops.sssd` role can be used to manage the System Security
  Services Daemon (``sssd``), an alternative approach to centralized
  credentials managed by remote databases like LDAP or Active Directory.

General
~~~~~~~

- The new :file:`bootstrap-sss.yml` Ansible playbook can be used to provision
  a new host with LDAP support based on the :command:`sssd` service instead of
  the :command:`nslcd` and :command:`nscd` services.

- The :ref:`debops.apache` and :ref:`debops.nginx` roles will configure the
  managed websites to opt-out from the `Federated Learning of Cohorts`__ (FLoC)
  feature by default. This can be turned off on a site-by-site basis.

  .. __: https://github.com/WICG/floc

:ref:`debops.etckeeper` role
''''''''''''''''''''''''''''

- The :command:`etckeeper` script can be configured to send e-mail messages
  with changes to the system administrator.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- You can now configure the :command:`iptables` backend (``nft`` or ``legacy``)
  after installing :command:`ferm` service using the alternatives system. This
  might be needed on newer OS releases to keep :command:`ferm` usable.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- Added wrapper around :file:`manage.py` called :file:`netbox-manage` for
  NetBox power users.

:ref:`debops.global_handlers` role
''''''''''''''''''''''''''''''''''

- New global handlers available to roles:

  - ``Refresh host facts``: re-gather host facts using the ``setup`` Ansible
    module, required to ensure that Ansible has accurate information about the
    current host state.

  - ``Reload service manager``: update the :command:`init` daemon runtime
    configuration, useful when new services are added or their
    :command:`systemd` configuration changes.

  - ``Create temporary files``: ensure that files and directories created at
    system boot by tools like :command:`systemd-tmpfiles` are present on the
    host.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Buster netboot installer version
  has been updated to the next point release, 10.9.

- In the :ref:`debops.roundcube` role, the Roundcube version installed by
  default has been updated to ``1.4.11``.

- The :ref:`debops.elasticsearch`, :ref:`debops.kibana` and
  :ref:`debops.filebeat` roles were updated to use the :ref:`debops.extrepo`
  role to configure the Elastic.co APT repositories. This will result in
  installation of ES, Kibana and Filebeat 7.x versions by default on new
  installations; existing installations will not be automatically upgraded by
  the roles, but the packages themselves might be upgraded by other APT
  mechanisms.

- In the :ref:`debops.netbox` role, the NetBox version has been updated to
  ``v2.11.2``.

- In the :ref:`debops.owncloud` role, the Nextcloud version has been updated to
  ``v20.0``. ``19.0`` support has been dropped.

- The ``lxc_ssh.py`` connection plugin that enables management of LXC
  containers without the need of an :command:`sshd` server installed inside of
  the containers has been refreshed to get latest changes in the upstream
  project and make it work correctly on newer Ansible releases.

Continuous Integration
''''''''''''''''''''''

- The Vagrant provisioning script now installs Cryptography from the Debian
  archive instead of from PyPI.

- The :command:`ansible-lint` check will now use Ansible playbooks as the
  starting point to test the whole codebase. Roles and playbooks not included
  in the :file:`site.yml` playbook can be tested manually if needed.

:ref:`debops.authorized_keys` role
''''''''''''''''''''''''''''''''''

- The management of the SSH public keys has been redesigned. Instead of
  focusing on UNIX accounts with one or more keys, the role now focuses on
  separate public keys as "SSH identities" that are configured on one or more
  UNIX accounts. This should provide more flexibility in environments where
  small number of users utilizes large number of UNIX accounts, for example
  small development team with multiple applications deployed on separate
  accounts.

``debops.boxbackup`` role
'''''''''''''''''''''''''

- Some of the default variables in the role have been renamed to aoid using
  uppercase letters in variables.

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- The LDAP user filer has been changed to use the ``mailRecipient`` LDAP object
  class from the :ref:`mailservice LDAP schema <slapd__ref_mailservice>` to
  lookup mail accounts. Ensure that your LDAP directory has correct information
  before applying the change in production.

- If the LDAP entry of a mail user has the ``mailHomeDirectory`` attribute, it
  will be used to specify the mail home directory relative to the mail root
  directory, instead of generating one which depends on the domain and username
  of a given account.

:ref:`debops.lxc` role
''''''''''''''''''''''

- On hosts which use LXC v4.0.x, for example with Debian Bullseye as the
  operating system, the role will configure new LXC containers to not drop the
  ``CAP_SYS_ADMIN`` capability by default. This is required for correct
  container operation on this version of LXC.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- ownCloud is not supported in the latest version of DebOps due to lack of
  maintainers. Use DebOps v2.2.x if you need it and consider becoming a
  maintainer.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- The :command:`autopostgresqlbackup` script will not be installed on Debian
  Bullseye because the package was dropped from that release.

:ref:`debops.postldap` role
'''''''''''''''''''''''''''

- The Postfix LDAP integration is redesigned to use the :ref:`mailservice LDAP
  schema <slapd__ref_mailservice>` for account and mailbox management. There
  are extensive changes in how the Postfix service utilizes the LDAP directory;
  existing installations will have to update their LDAP directory entries.
  Please test these changes in a development environment before applying them
  in production.

:ref:`debops.python` role
'''''''''''''''''''''''''

- The support for Python 2.7 environment will be enabled only when explicitly
  requested using the :envvar:`python__v2` variable. This should avoid issues
  with installation of Python 2.7 packages on Debian Bullseye and later.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- The address autocompletion will show only a specific e-mail address instead
  of all available ones for a given recipient.

- The role will configure Roundcube to search the LDAP directory for a given
  user's Distinguished Name when their LDAP entry uses a different attribute
  than ``uid`` as RDN. Directory will be searched using the Roundcube's own
  login credentials. See :ref:`roundcube__ref_ldap_dit` for details.

- The ``new_user_identity`` plugin will be re-enabled by default and adjusted
  to use the ``mail`` attribute to search for user identities. Roundcube v1.4.x
  installations `might need to be patched`__ for the plugin to work correctly
  with user-based LDAP logins.

  .. __: https://github.com/roundcube/roundcubemail/issues/7667

:ref:`debops.saslauthd` role
''''''''''''''''''''''''''''

- The SMTPd service will search for ``mailRecipient`` LDAP Object Class instead
  of the ``inetOrgPerson`` Object Class to authenticate mail senders.

Changes to DebOps Enhancement Proposals
'''''''''''''''''''''''''''''''''''''''

- DEP 3 - Sources of software used by DebOps now requires for roles that
  configure upstream APT repositories to use ``debops.extrepo`` instead of the
  previously used way of including the OpenPGP fingerprint and repo details in
  the role. This applies to all new roles. Existing roles will be updated over
  time.

Fixed
~~~~~

General
'''''''

- The :command:`debops-defaults` script should now correctly display role
  defaults, without trying to add the ``debops.`` prefix to the role names.

- The :command:`debops-update` script should now correctly detect cloned DebOps
  monorepo.

- The :command:`debops` script will no longer check Ansible version to work
  around an issue that was fixed in Ansible 2.0.

:ref:`debops.ansible_plugins` role
''''''''''''''''''''''''''''''''''

- In the ``parse_kv_config`` custom Ansible filter, correctly skip
  configuration entries which have been marked with the ``ignore`` state.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role configured the Debian Bullseye security repository with the
  'bullseye/updates' suite name. This is incorrect, the Bullseye security suite
  is called 'bullseye-security'.

:ref:`debops.core` role
'''''''''''''''''''''''

- Fixed local fact script execution on hosts without a defined DNS domain. You
  might need to remove the :file:`core.fact` script from the remote host
  manually so that Ansible can gather facts correctly before the fixed version
  of the script can be installed. To do that on all affected hosts, execute the
  command:

  .. code-block:: console

     ansible all -b -m file -a 'path=/etc/ansible/facts.d/core.fact state=absent'

:ref:`debops.cron` role
'''''''''''''''''''''''

- Fix role execution on hosts without :command:`systemd` as the service manager.

:ref:`debops.etesync` role
''''''''''''''''''''''''''

- The EteSync playbook is now included in the default DebOps playbook.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The management of the :command:`iptables` backend symlink using the
  'alternatives' system is disabled on Debian 9, where it is unsupported.

:ref:`debops.iscsi` role
''''''''''''''''''''''''

- Fixed a typo that caused the iSCSI target discovery task to fail.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- NetBox crashed when it tried to send Emails.
  For example when an exception occurred during page loading, the response was
  just "Internal Server Error". The service as a whole survives this.
  The bug in the configuration template has been fixed.

:ref:`debops.opendkim` role
'''''''''''''''''''''''''''

- Restored compatibility with Ansible versions prior to 2.10 by omitting the
  ``regenerate`` parameter of the openssl_privatekey module on those versions.

:ref:`debops.pki` role
''''''''''''''''''''''

- The pki-realm script will now attempt another ACME certificate request in case
  the previous attempt failed and was more than two days ago. The previous
  situation was that the script would not perform any ACME requests if the
  acme/error.log file was present in the PKI realm, because performing multiple
  certificate issuance requests could easily trigger a rate limit. The downside
  of this was that the script would also completely give up on renewal attempts
  if the first attempt happened to fail (e.g. due to some issue at Let's
  Encrypt).

:ref:`debops.php` role
''''''''''''''''''''''

- Fixed an issue where role did not have a list of PHP packages for an unknown
  OS release which stopped its execution. Now the role should fallback to
  a default list in this case.

:ref:`debops.python` role
'''''''''''''''''''''''''

- Fixed an issue where the "raw" Python play used during host bootstrapping
  hanged indefinitely, stopping the playbook execution. The role will now reset
  the connection to the host after preparing the Python environment, allowing
  Ansible to re-estabilish the communication channel properly.

:ref:`debops.saslauthd` role
''''''''''''''''''''''''''''

- The :command:`saslauthd` daemon should correctly use the local and realm
  parts in the ``user@realm`` logins for authentication using LDAP directory.

:ref:`debops.sudo` role
'''''''''''''''''''''''

- The role no longer adds a duplicate includedir line to /etc/sudoers. This was
  an issue with sudo 1.9.1 (and later), which `changed`__ the includedir syntax
  from '#includedir' to '\@includedir'.

  .. __: https://www.sudo.ws/stable.html#1.9.1

- Use the English locale to read the :command:`sudo` version information since
  the output differs in different languages.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- Use the Python version detected on the Ansible Controller instead of the
  remote host to run the UNIX account fact gathering script.

Security
~~~~~~~~

:ref:`debops.hashicorp` role
''''''''''''''''''''''''''''

- Due to a `security incident`__, the existing Hashicorp release GPG key has
  been rotated. The role will remove the revoked GPG key and install new one
  when applied on a host.

  .. __: https://discuss.hashicorp.com/t/hcsec-2021-12-codecov-security-event-and-hashicorp-gpg-key-exposure/23512


`debops v2.2.0`_ - 2021-01-31
-----------------------------

.. _debops v2.2.0: https://github.com/debops/debops/compare/v2.1.0...v2.2.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.dhcrelay` role can be used to manage the ISC DHCP Relay
  Agent, which forwards DHCP traffic between networks. This role replaces the
  dhcrelay functionality in :ref:`debops.dhcpd`.

- The :ref:`debops.global_handlers` Ansible role provides a central place to
  maintain handlers for other Ansible roles. Keeping them centralized allows
  Ansible roles to use handlers from different roles without including them
  entirely in the playbook.

- The :ref:`debops.filebeat` role can be used to install and configure
  `Filebeat`__, a log shipping agent from Elastic, part of the Elastic Stack.

  .. __: https://www.elastic.co/beats/filebeat

General
'''''''

- The :file:`tools/reboot.yml` can be used to reboot DebOps hosts even if they
  are secured by the ``molly-guard`` package.

- The code in the DebOps monorepo is now checked using `GitHub Actions`__,
  which will replace Travis-CI. Thank you, Travis, for years of service. :)

  .. __: https://github.com/features/actions

LDAP
''''

- The :ref:`next available UID and GID values <ldap__ref_next_uid_gid>` can now
  be tracked using special LDAP objects in the directory. These can be used by
  the client-side account and group management applications to easily allocate
  unique UID/GID numbers for newly created accounts and groups.

  The objects will be created automatically with the next available UID/GID
  values by the :file:`ldap/init-directory.yml` playbook. In existing
  environments users might want to create them manually to ensure that the
  correct ``uidNumber`` and ``gidNumber`` values are stored instead of the
  default ones which might already be allocated.

- The ``root`` UNIX account will now have full write access to the main
  directory via the ``ldapi://`` external authentication and can create and
  modify the LDAP objects and their attributes. This is required so that the
  :ref:`debops.slapd` role can initialize the directory tree and create/remove
  the ACL test objects as needed.

:ref:`debops.apt` role
''''''''''''''''''''''

- The role facts now include the main APT architecture (``amd64``, for example)
  and a list of foreign architectures if any are enabled. The
  ``ansible_local.apt.architecture`` fact can be used in other roles that need
  that information.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The role now installs CPU microcode packages on physical hosts by default.
  These firmware updates correct CPU behaviour and mitigate vulnerabilities like
  Spectre and Meltdown. You still need to take measures to protect your virtual
  machines; for this, take a look at the `QEMU documentation`__.

  .. __: https://www.qemu.org/docs/master/system/target-i386.html#important-cpu-features-for-intel-x86-hosts

:ref:`debops.icinga` role
'''''''''''''''''''''''''

- The role can now create Icinga configuration on the Icinga "master" node via
  task delegation. This can be useful in centralized environments without
  Icinga Director support.

:ref:`debops.lvm` role
''''''''''''''''''''''

- Default LVM2 configuration for Debian Stretch and Buster has been added.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Drop Nextcloud 16, 17 and 18 support because it is EOL. You need to upgrade Nextcloud
  manually if you are running version 18 or below. The role now defaults to
  Nextcloud 19 for new installations.

:ref:`debops.postgresql` role
'''''''''''''''''''''''''''''

- The role can now drop PostgreSQL databases and remove roles when their state
  is set to ``absent`` in the Ansible inventory.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- Support manipulating file privileges using the Linux
  :manpage:`capabilities(7)` with the help of the Ansible capabilities
  module.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- The role will enable more plugins by default: ``help``, ``markasjunk``,
  ``password`` (only with LDAP).

- Roundcube will offer local spell checking support by default with ``Enchant``
  library. English language is supported by default, more languages can be
  added via Ansible inventory.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Support for the dynamic LDAP groups maintained by the
  :ref:`slapd__ref_autogroup_overlay` has been implemented in the role. Debian
  Buster or newer is recommended for this feature to work properly.

- A set of `FreeRADIUS`__ LDAP schema has been added to the role. RADIUS
  Profiles, Clients and FreeRADIUS DHCP configuration can be stored in the LDAP
  directory managed by DebOps and used by the :ref:`debops.freeradius` Ansible
  role.

  .. __: https://freeradius.org/

- Support for empty LDAP groups has been added via the :ref:`groupfentries
  schema <slapd__ref_groupofentries>` with a corresponding ``memberOf``
  overlay. This change changes the order of existing overlays in the LDAP
  database which means that the directory server will have to be rebuilt.

- New :ref:`orgstructure schema <slapd__ref_orgstructure_schema>` provides the
  ``organizationalStructure`` LDAP object class which is used to define the
  base directory objects, such as ``ou=People``, ``ou=Groups``, etc.

- Members of the ``cn=LDAP Administrator`` LDAP role can now manage the server
  configuration stored in the ``cn=config`` LDAP subtree.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The role can now be enabled or disabled conditionally via Ansible inventory.
  This might be required in certain cases, for example LXD containers or
  systems protected with AppArmor rules, which make the :file:`/proc/sys/`
  directory read-only.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Stretch and Debian Buster netboot
  installer versions have been updated to their next point releases, 9.13 and
  10.7 respectively.

- In the :ref:`debops.roundcube` role, the Roundcube version installed by
  default has been updated to ``1.4.10``.

- In the :ref:`debops.owncloud` role, the Nextcloud version installed by
  default has been updated to ``v18.0``.

- In the :ref:`debops.phpipam` role, the phpIPAM version installed by default
  has been updated to ``v1.4.1``.

- In the :ref:`debops.netbox` role, the NetBox version has been updated to
  ``v2.10.3``.
  The plugin support added in ``v2.8.0`` can be configured from DebOps.
  The NetBox Request Queue Worker service is configured to support background
  jobs like reports to work.

- The :ref:`debops.mariadb` and :ref:`debops.mariadb_server` roles now support
  installation of Percona Server/Client v8.0 from upstream APT repositories.

General
'''''''

- The ``debops.debops`` role has been renamed to the :ref:`debops.controller`
  role to allow for the ``debops__`` variable namespace to be used for global
  variables. All role variables have been renamed along with the role inventory
  group, you will have to update your inventory.

- Most of the handers from different DebOps roles have been moved to the new
  :ref:`debops.global_handlers` role to allow for easier cross-role handler
  notification. The role has been imported in roles that rely on the handlers.

- The ``debops-contrib.*`` roles included in the DebOps monorepo have been
  renamed to drop the prefix. This is enforced by the new release of the
  :command:`ansible-lint` linter. These roles are not yet cleaned up and
  integrated with the main playbook.

- The dependency on ``pyOpenSSL`` has been removed. This dependency was required
  in Ansible < 2.8.0 because these versions were unable to use the
  ``cryptography`` module, but DebOps is nowadays developed against Ansible 2.9.
  pyOpenSSL was used only to generate private RSA keys for the
  :ref:`debops.opendkim` role. Switching to ``cryptography`` is also a security
  precaution and the Python Cryptographic Authority
  `recommends`__ doing so.

  .. __: https://github.com/pyca/cryptography/blob/master/docs/faq.rst#why-use-cryptography)

LDAP
''''

- The :ref:`LDAP-POSIX integration <ldap__ref_posix>` can now be disabled using
  a default variable. This will disable LDAP support in the POSIX environment
  and specific services (user accounts, PAM, :command:`sshd`, :command:`sudo`)
  while leaving higher-level services unaffected.

- The LDAP directory structure creation has been moved from a separate
  :file:`ansible/playbooks/ldap/init-directory.yml` playbook into the
  :ref:`debops.slapd` role to allow for better ACL testing. The playbook is
  still used for administrator account creation.

- The base directory objects created by the :ref:`debops.slapd` role
  (``ou=People``, ``ou=Groups``, etc.) as well as other DebOps roles
  (:ref:`debops.dokuwiki`, :ref:`debops.ldap`, :ref:`debops.postldap`) changed
  their structural object type from ``organizationalUnit`` to
  ``organizationalStructure``. Existing directories should not be affected by
  this change, but users might want to update them using the :ref:`backup and
  restore procedure <slapd__ref_backup_restore>` to allow for more extensive
  ACL rules in the future.

:ref:`debops.core` role
'''''''''''''''''''''''

- The fact script will generate the list of private e-mail addresses used to
  send administrative mail notifications based on the list of admin accounts
  and the detected domain of the host; this can be overridden via the
  :envvar:`core__admin_private_email` variable. The change is done to avoid
  sending mail messages to 'account-only' addresses on hosts without local mail
  support.

:ref:`debops.dhcpd` role
''''''''''''''''''''''''

- The ``debops.dhcpd`` role has been largely rewritten in order to support
  both IPv4 and IPv6 on the same server, and to modernize many aspects of the
  role.

- The DHCP Relay Agent functionality has been moved to :ref:`debops.dhcrelay`.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- The role's virtual environment is no longer created by default when
  :envvar:`docker_server__upstream` is ``False``. This does not impact existing
  virtualenvs. You can remove ``/usr/local/lib/docker/virtualenv`` yourself if
  you like.

:ref:`debops.etckeeper` role
''''''''''''''''''''''''''''

- The role now installs etckeeper on all hosts by default, not just on hosts
  that have a Python 2 environment. etckeeper is also installed from
  buster-backports instead of the main Debian 10 repository.

:ref:`debops.fhs` role
''''''''''''''''''''''

- The role will create the :file:`/srv/www/` directory by default to allow for
  home directories used by web applications.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The :command:`systemd` services no longer require Redis to be installed on
  the same host as GitLab itself.

- Improved support for GitLab Pages, including optional access control and
  fixed configuration of the :command:`systemd` service.

:ref:`debops.grub` role
'''''''''''''''''''''''

- The role will now activate both the serial console and the (previously
  disabled) native platform console when ``grub__serial_console`` is ``True``.

:ref:`debops.icinga_web` role
'''''''''''''''''''''''''''''

- The role now automatically configures LDAP user and group support.

- The role will install and configure the `Icinga Certificate Monitoring`__
  module.

  .. __: https://icinga.com/docs/icinga-certificate-monitoring/latest/

:ref:`debops.lvm` role
''''''''''''''''''''''

- Linux Software RAID devices are now scanned by default.

:ref:`debops.lxd` role
''''''''''''''''''''''

- During installation, the role will enable trust for the GitHub's GPG signing
  key to allow for verification of the LXD source code. Check the
  :ref:`lxd__ref_install_details` for more information.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The default SSL configuration used by the role has been updated to bring it
  to the modern standards. By default only TLSv1.2 and TLSv1.3 protocols are
  enabled, along with an improved set of ciphers. The HTTP Strict Transport
  Security age has been increased from 6 months to 2 years. The configuration
  is based on the `intermediate Mozilla SSL recommendations`__ to support wide
  range of possible clients.

  .. __: https://ssl-config.mozilla.org/#server=nginx&version=1.17.7&config=intermediate&openssl=1.1.1d&guideline=5.6

- The server can be configured to support TLSv1.3 protocol only using the
  :envvar:`nginx_default_tls_protocols` variable, which will disable the use of
  custom Diffie-Hellman parameters and allow the HTTPS clients to select their
  own preferred ciphers to use for connections. The preferred set of ciphers
  will also change to `Mozilla modern`__ variant. Keep in mind that not all
  clients support this configuration.

  .. __: https://ssl-config.mozilla.org/#server=nginx&version=1.17.7&config=modern&openssl=1.1.1d&guideline=5.6

:ref:`debops.postfix` role
''''''''''''''''''''''''''

- Postfix :file:`main.cf` configuration overrides are now written to the
  :file:`master.cf` configuration file using 'long form' notation supported
  since Postfix 3.0. This allows specifying parameter values that contain
  whitespace.

- The `DSN command`__ is now disabled by default. DSN (:rfc:`3464`) gives
  senders control over successful and failed delivery status notifications. This
  allows spammers to learn about an organization's internal mail infrastructure,
  and gives them the ability to confirm that an address is in use. When DSN
  support is disabled, Postfix will still let the SMTP client know that their
  message has been received as part of the SMTP transaction; they just will not
  get successful delivery notices from your internal systems.

  .. __: http://www.postfix.org/DSN_README.html

- The `ETRN command`__ is now disabled by default. ETRN, also known as Remote
  Message Queue Starting (:rfc:`1985`), was designed for sites that have
  intermittent Internet connectivity, but is rarely used nowadays.

  .. __: http://www.postfix.org/ETRN_README.html

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- The 'domain', 'nameservers' and 'search' variables have been removed from the
  resolvconf Ansible local facts script. You are encouraged to use the
  `ansible_domain`, `ansible_dns.nameservers` and `ansible_dns.search` variables
  instead.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The role will set up an additional instance of the ``memberof`` OpenLDAP
  overlay to update role membership in the ``organizationalRole`` LDAP objects.
  This change modifies the list of overlays and will require re-initialization
  of the OpenLDAP directory.

- New equality indexes have been added to the :command:`slapd` service:
  ``roleOccupant``, ``memberOf`` and ``employeeNumber``.

- The :file:`eduperson.schema` LDAP schema has been extended with additional
  attributes not present in the official specification. The new schema will not
  be applied automatically on existing installations.

- In the OpenLDAP ACL rules, authenticated object owners can now
  re-authenticate themselves using the ``userPassword`` attribute. This is
  needed for the LDAP Password Modify Extended Operation (:rfc:`3062`) to work
  correctly in Roundcube.

- In the :file:`mailservice.schema` LDAP schema, the ``mailACLGroups``
  attribute has been renamed to ``mailGroupACL`` since this seems to be the
  name used by different applications like Dovecot and Roundcube.

  This change will not be applied automatically in an existing LDAP directories
  - they will need to be rebuilt to apply new schema changes.

- The role will install a modified :ref:`OpenSSH-LPK schema
  <slapd__ref_openssh_lpk>` instead of the version from the FusionDirectory
  project, to add support for storing SSH public key fingerprints in the LDAP
  directory. Existing installations shouldn't be affected.

- The :command:`slapacl` test map with additional object RDNs has been
  redesigned into a list of test LDAP objects which can be created or removed
  by the role as needed. They will not be added to the directory by default and
  can be enabled via Ansible inventory.

- The support for OpenLDAP monitoring is improved. The ``root`` UNIX account as
  well as members of the "LDAP Administrator" and "LDAP Monitor" roles can now
  read the ``cn=Monitor`` information.

Removed
~~~~~~~

:ref:`debops.ldap` role
'''''''''''''''''''''''

- Creation of various LDAP directory objects (``ou=People``, ``ou=Groups``,
  ...) has been removed from the default list of LDAP tasks performed by the
  role. These objects are now automatically created by the :ref:`debops.slapd`
  role. The :ref:`debops.ldap` role will still ensure that all LDAP objects
  needed to maintain the hosts' directory information are present.

Fixed
~~~~~

General
'''''''

- Fixed an issue where the :command:`debops` scripts did not expand the
  :file:`~/` prefix of the file and directory paths in user home directories.

- Fixed an issue with custom lookup plugins (:file:`task_src`,
  :file:`file_src`, :file:`template_src`) which resulted in Ansible 2.10 not
  finding them correctly.

LDAP
''''

- The :file:`ldap/init-directory.yml` playbook will correctly initialize the
  LDAP directory when the local UNIX account does not have any GECOS
  information.

:ref:`debops.apt` role
''''''''''''''''''''''

- Fixed an issue where the role would attempt to add APT keys from a PGP
  keyserver without installing the :command:`gnupg` package first.

:ref:`debops.dokuwiki` role
'''''''''''''''''''''''''''

- A few custom DokuWiki plugins will be removed if installed, otherwise they
  will not be installed anymore due to issues with newest DokuWiki release.
  Affected plugins: ``advrack``, ``rst``, ``gitlab``, ``ghissues``.

- Ensure that the ``authldap`` DokuWiki plugin is enabled when LDAP support is
  configured by the role.

:ref:`debops.etherpad` role
'''''''''''''''''''''''''''

- Fixed the installation of Etherpad with the PostgreSQL backend by removing
  unused dependent variables.

:ref:`debops.fail2ban` role
'''''''''''''''''''''''''''

- Fixed the configuration support on Ubuntu Focal due to bantime feature
  changes in the :command:`fail2ban` v0.11.

:ref:`debops.fcgiwrap` role
'''''''''''''''''''''''''''

- The role can now be used in check mode without throwing an AnsibleFilterError.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- Fixed an issue where the ``git`` UNIX account was not added to the
  ``_sshusers`` local group when LDAP support was enabled on the host. This
  prevented the usage of GitLab via SSH.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- Network configuration with bonded interfaces should now be correctly applied
  by the reconfiguration script.

:ref:`debops.iscsi` role
''''''''''''''''''''''''

- Fixed uninitialized local fact ``ansible_local.iscsi.discovered_portals``.

:ref:`debops.ldap` role
'''''''''''''''''''''''

- Fixed multiple issues with adding and updating hosts to the LDAP directory
  when these hosts were configured for network bonding.

:ref:`debops.lvm` role
''''''''''''''''''''''

- Fixed an issue where the role would fail in check mode. The role tries to
  simulate creating a filesystem, but this failed when the underlying LVM volume
  did not actually exist (which is to be expected when running in check mode).

- Made default behaviour match the documentation: the role now automatically
  takes care of mounting a filesystem on an LVM volume if the mount point is
  specified with ``item.mount``. This previously required setting the
  ``item.fs`` parameter to ``True`` as well.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Disabled gzip compression of text/vcard MIME types. Vcards contain, by nature,
  sensitive information and should not be gzipped to prevent successful BREACH
  attacks.

:ref:`debops.netbox` role
'''''''''''''''''''''''''

- Fixed initial superuser account creation.

:ref:`debops.nslcd` role
''''''''''''''''''''''''

- Enabled idle_timelimit to make sure that connections to the LDAP server are
  properly closed. A disabled or too high idle_timelimit causes the LDAP server
  to time out, resulting in nslcd errors like "ldap_result() failed: Can't
  contact LDAP server".

:ref:`debops.nfs` role
''''''''''''''''''''''

- Ensure that with default mount options disabled, options specified by the
  user still are added in the configuration.

:ref:`debops.ntp` role
''''''''''''''''''''''

- Don't try to disable or stop the ``systemd-timesyncd`` service when using an
  alternative NTP service implementation and ``systemd-timesyncd`` is not
  available.

:ref:`debops.owncloud` role
''''''''''''''''''''''''''''

- Fixed multiple issues which caused dry runs of the :ref:`debops.owncloud` role
  to incorrectly show pending changes or fail altogether.

:ref:`debops.php` role
''''''''''''''''''''''

- Set correct APT preferences for the Backports or Sury APT repository to
  the ``libapache2-mod-php*`` APT packages to ensure that the selected
  repository is the same as the ``php*`` APT packages.

:ref:`debops.pki` role
''''''''''''''''''''''

- The :command:`acme-tiny` script will be installed from Debian/Ubuntu
  repositories on Debian Buster, Ubuntu Focal and newer OS releases. This
  solves the issue with ``acme-tiny`` script in upstream having
  ``#!/usr/bin/env python`` shebang hard-coded which makes the script unusable
  on hosts without Python 2.7 installed.

  The installation location of the script from upstream is changed from
  :file:`/usr/local/lib/pki/` to :file:`/usr/local/bin/` to leverage the
  ``$PATH`` variable so that the OS version is used without issues. The script
  is now also symlinked into place instead of copied over.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- Rename the ``wal_keep_segments`` PostgreSQL configuration option to
  ``wal_keep_size`` on PostgreSQL 13 and later to avoid issues with starting
  the database service. You might need to update the inventory configuration if
  you use this parameter.

- Fixed an issue with the role always reporting "changed" state due to
  ``postgresql_privs`` Ansible module not detecting changes in the ``PUBLIC``
  PostgreSQL role.

:ref:`debops.python` role
'''''''''''''''''''''''''

- The ``python-pip`` APT package will be installed only on older OS releases,
  since it has been removed from newer OS releases like Debian Bullseye and
  Ubuntu Focal.

:ref:`debops.rsnapshot` role
''''''''''''''''''''''''''''

- Fixed an issue which caused dry runs of the :ref:`debops.rsnapshot` role to
  fail.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- Fixed the forgotten :envvar:`rsyslog__send_permitted_peers` variable which
  defines what server is accepted by the client during TLS handshakes. The
  value will now be defined using the ``streamDriverPermittedPeers`` parameter
  in :command:`rsyslog` configuration.

:ref:`debops.saslauthd` role
''''''''''''''''''''''''''''

- Fixed SMTP AUTH e-mail authentication for satellite hosts. Mail messages sent
  by :command:`nullmailer` and authenticated using LDAP should now be accepted
  by the SMTP server.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Modify the :file:`mailservice.schema` LDAP schema so that various
  mail-related attributes do not use the ``mail`` attribute as SUPerior
  attribute. This fixes an issue where searching for ``mail`` attribute values
  returned entries with the values present in related attributes, for example
  ``mailForwardTo``, causing problems with account lookups.

  This change will require the rebuild of the OpenLDAP directory to be applied
  correctly. The role will not apply the changes on existing installations
  automatically due to the :file:`mailservice.schema` being loaded into the
  database.

- The :command:`slapd-snapshot` script will now correctly create database
  snapshots when the ``cn=Monitor`` database is disabled or not configured.

:ref:`debops.snmpd` role
''''''''''''''''''''''''

- Don't create or modify the home directory of the :command:`snmpd` UNIX
  account to avoid issues on Ubuntu 20.04.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- Fixed an issue where the role execution broke if the
  :envvar:`system_users__self_name` variable was set to an UNIX account which
  does not exist on the Ansible Controller, for example ``ansible``. The role
  will now correctly create such UNIX accounts on the remote hosts with default
  GECOS and shell values.

:ref:`debops.tinc` role
'''''''''''''''''''''''

- Fix issue with Tinc VPN interfaces starting before the general host
  networking is set up and failing to bind to the selected bridge interface.
  The Tinc :command:`systemd` service will wait for the
  ``network-online.target`` unit to start up before activation.

- Fixed an issue with the role where setting :envvar:`tinc__modprobe` variable
  to ``False`` did not turn off support for loading required kernel modules.


`debops v2.1.0`_ - 2020-06-21
-----------------------------

.. _debops v2.1.0: https://github.com/debops/debops/compare/v2.0.0...v2.1.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.etesync` role allows to setup a EteSync__ server.
  EteSync is a cross-platform project to provide secure, end-to-end encrypted,
  and privacy respecting sync for your contacts, calendars and tasks.

.. __: https://www.etesync.com/

- The :ref:`debops.journald` role can be used to manage the
  :command:`systemd-journald` service, supports configuration of Forward Secure
  Sealing and can configure persistent storage of the log files. The role is
  included by default in the :file:`common.yml` playbook.

- The :ref:`debops.dpkg_cleanup` role can create :command:`dpkg` hooks that
  help clean up custom and diverted files created by other roles when a given
  Debian package is removed. This should aid in cases of multiple roles
  managing services that provide the same functionality.

- The :ref:`debops.influxdata` role configures the APT repository and
  repository GPG keys of `InfluxData`__ company, creator of InfluxDB, Telegraf
  and other metric and time series tools.

  .. __: https://influxdata.com/

- The :ref:`debops.influxdb_server` and :ref:`debops.influxdb` roles can be
  used to install the InfluxDB time series database service and manage its
  databases and users, respectively.

- The :ref:`debops.fhs` role will be used to define base directory hierarchy
  used by other DebOps roles (previously done by the :ref:`debops.core` role).
  The role is included in the :file:`common.yml` playbook.

- The :ref:`debops.tzdata` role manages the host time zone configuration and
  provides the ``ansible_local.tzdata.timezone`` local fact with the time zone
  in the ``Area/Zone`` format. The role is included in the :file:`common.yml`
  playbook.

:ref:`debops.pki` role
''''''''''''''''''''''

- The role can now instruct acme-tiny to register an ACME account with one or
  more contact URLs. Let's Encrypt for example uses this information to notify
  you about expiring certificates and emergency revocation.

- The :ref:`debops.dovecot` and :ref:`debops.postfix` roles now include the PKI
  hook scripts which will reload their corresponding services when the X.509
  certificates used by them are changed.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- The additional Postfix configuration managed by the role can now be added or
  removed conditionally, controlled by the :envvar:`postconf__deploy_state`
  variable.

:ref:`debops.python` role
'''''''''''''''''''''''''

- Introduce :envvar:`python__pip_version_check` which defaults to ``False`` to
  disable PIP update checks outside of the system package manager.
  Before, this was not configured by DebOps leaving it at PIP default which
  meant it would check for updates occasionally.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- Add support for the ``access_time`` and ``modification_time`` parameters of
  the Ansible file module to the role.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- The role can now be configured to install Roundcube from private or internal
  :command:`git` repositories that might contain additional modifications to
  the application code required by some organizations. See the
  :ref:`roundcube__ref_private_repo` section in the documentation for details.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Stretch and Debian Buster netboot
  installer versions have been updated to their next point releases, 9.11 and
  10.4 respectively.

- In the :ref:`debops.owncloud` role, the Nextcloud version installed by
  default has been updated to ``v17.0``. The ownCloud version has been updated
  to ``v10.4``.

- In the :ref:`debops.roundcube` role, the Roundcube version installed by
  default has been updated to ``v1.4.4``.

- In the :ref:`debops.lxd` role, the LXD version installed by default has been
  changed to the ``stable-4.0`` branch, which is a LTS release. The role uses
  a :command:`git` branch instead of a specific tagged release to bypass
  `broken LXD build dependency`__ which is not yet fixed in a tagged release.

  .. __: https://github.com/lxc/lxd/issues/7357

- In the :ref:`debops.gitlab` role, the GitLab release installed on Debian
  Buster and newer OS releases is updated to ``12-10-stable``.

  This release requires Golang packages from ``buster-backports`` APT
  repository, which will be installed by default via the :ref:`debops.golang`
  role. Existing installations need to upgrade the Golang packages before the
  playbook is applied.

- In the :ref:`debops.ansible` role, Ansible 2.9.x from the
  ``buster-backports`` repository will be installed on Debian Buster by
  default, when backports are enabled.

- The :ref:`debops.mailman` role has been redesigned and now installs and
  configures Mailman 3.x instead of Mailman 2.x. Read the
  :ref:`mailman__ref_mailman2_migration` guide and the rest of the
  :ref:`debops.mailman` documentation for details.

Continuous Integration
''''''''''''''''''''''

- The Vagrant provisioning script will install Ansible from PyPI by default.
  The version included in the current Debian Stable (Buster) is too old for the
  DebOps playbooks and roles.

General
'''''''

- The DebOps Collection published on Ansible Galaxy has been split into
  multiple Collections due to the number of Ansible roles present in DebOps.
  The ``debops.debops`` collection will install additional ``debops.rolesXY``
  collections automatically via collection dependencies. The playbooks have
  been updated to include new Collections.

- The DebOps repository is now compliant with the `REUSE Specification`__. The
  `SPDX License Identifiers`__ have been added to the files contained in the
  repository and a valid copyright and license information will be required to
  pass the test suite.

  .. __: https://reuse.software/spec/
  .. __: https://spdx.org/ids

- In new DebOps environments, Ansible will ignore any missing inventory groups
  using the ``host_pattern_mismatch`` parameter. This will disable the "Could
  not match supplied host pattern" warning message present in most of the
  playbooks included in DebOps. To disable this message in an existing
  environment, add in the :file:`.debops.cfg` configuration file:

  .. code-block:: ini

     [ansible inventory]
     host_pattern_mismatch = ignore

- The :command:`debops` script will now use the Ansible inventory path defined
  in the :file:`.debops.cfg` configuration file ``[ansible defaults]`` section
  instead of the static :file:`ansible/inventory/` path.

- The variables in various DebOps roles that define filesystem paths have been
  switched from using the ``ansible_local.root.*`` Ansible local facts to the
  new ``ansible_local.fhs.*`` facts defined by the :ref:`debops.fhs` role.
  The new facts use the same base paths as the old ones; there should be no
  issues if the variables have not been modified through Ansible inventory.

  If you have redefined any ``core__root_*`` variables in the Ansible inventory
  to modify the filesystem paths used by DebOps roles, you will need to update
  the configuration. See the :ref:`debops.fhs` role documentation for details.

- The use of ``ansible_local.core.fqdn`` and ``ansible_local.core.domain``
  local facts in roles to define the host DNS domain and FQDN has been removed;
  the roles will use the ``ansible_fqdn`` and ``ansible_domain`` facts
  directly. This is due to issues with the :ref:`debops.core` local facts not
  updating when the host's domain is changed and causing the roles to use wrong
  domain names in configuration.

:ref:`debops.cran` role
'''''''''''''''''''''''

- The custom ``cran`` Ansible module used by the role has been moved to the
  :ref:`debops.ansible_plugins` role to allow it to be used via Ansible
  Collection system, which requires all plugins to be centralized.

:ref:`debops.etc_aliases` role
''''''''''''''''''''''''''''''

- The custom filter plugin used by the role has been moved to the
  :ref:`debops.ansible_plugins` role to allow it to be used via Ansible
  Collection system, which requires all plugins to be centralized.

:ref:`debops.golang` role
'''''''''''''''''''''''''

- On Debian Buster, Golang APT packages from the ``buster-backports`` APT
  repository will be preferred instead of their Buster version. This allows for
  installation of applications that depend on a newer Go runtime environment,
  like GitLab or MinIO.

:ref:`debops.lxd` role
''''''''''''''''''''''

- The support for the LXC containers managed by the :ref:`debops.lxc` role will
  be applied on the host when the LXD is configured, due to the build
  dependency on the ``lxc`` APT package. In this case, the ``lxcbr0`` network
  bridge will not be configured by default.

:ref:`debops.mosquitto` role
''''''''''''''''''''''''''''

- Update the role for Debian Buster. No need anymore to install Python packages
  outside of the system package management.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- TLSv1.3 is now enabled by default for nginx version 1.13.0 and up.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- The Nullmailer smtpd service can now listen on both IPv4 and IPv6 addresses.
  It listens on both loopback addresses by default, where it used to only
  listen on the IPv6 loopback address.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Support has been added for Nextcloud 17.0 and 18.0.

:ref:`debops.pki` role
''''''''''''''''''''''

- Use ``inventory_hostname`` variable instead of the ``ansible_fqdn`` variable
  in paths of the directories used to store data on Ansible Controller. This
  decouples the host FQDN and domain name from the certificate management tasks
  in the role.

  .. note:: The role will try to recreate existing X.509 certificates making
            the playbook execution idempotent. Removing the PKI realms and
            recreating them will fix this issue.

:ref:`debops.postfix` role
''''''''''''''''''''''''''

- The persistent configuration stored on the Ansible Controller has been
  refactored and does not use multiple separate tasks to handle the JSON files.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- The role has been refreshed and uses the custom Ansible filter plugins to
  manage the :command:`rsyslog` configuration files. The default configuration
  was rearranged, the :file:`/etc/rsyslog.conf` configuration file has the
  default contents that come with the Debian package and can be configured by
  the role. The configuration model has been redesigned; any changes in the
  configuration of the role set in the Ansible inventory need to be reviewed
  before applying the new version.

- The ``rsyslog`` APT package and its service can be cleanly removed from the
  host, either via the role or by uninstalling the package itself.

Removed
~~~~~~~

:ref:`debops.console` role
''''''''''''''''''''''''''

- The local and NFS mount support has been removed from the
  :ref:`debops.console` role. Local mounts can be managed using the
  :ref:`debops.mount` role; NFS mounts can be managed by the :ref:`debops.nfs`
  role.

:ref:`debops.core` role
'''''''''''''''''''''''

- The ``ansible_local.uuid`` local fact and corresponding variables and tasks
  have been removed from the role. A replacement fact, ``ansible_machine_id``
  is an Ansible built-in.

- The ``ansible_local.init`` fact has been removed from the role. A native
  ``ansible_service_mgr`` Ansible fact is it's replacement.

- The ``ansible_local.cap12s`` fact has been removed from the role. A native
  set of Ansible facts (``ansible_system_capabilities``,
  ``ansible_system_capabilities_enforced`` is be used as a replacement.

- The :file:`root.fact` script, corresponding variables and documentation have
  been removed from the role. This functionality is now managed by the
  :ref:`debops.fhs` role.

- The ``ansible_local.core.fqdn`` and ``ansible_local.core.domain`` local facts
  and their corresponding default variables have been removed from the role. In
  their place, ``ansible_fqdn`` and ``ansible_domain`` facts should be used
  instead.

:ref:`debops.ntp` role
''''''''''''''''''''''

- The timezone configuration has been moved from the :ref:`debops.ntp` role to
  the :ref:`debops.tzdata` role.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- The script and :command:`dpkg` hook that cleaned up the additional files
  maintained by the role has been removed; the :ref:`debops.dpkg_cleanup` role
  will be used for this purpose instead.

Fixed
~~~~~

General
'''''''

- Fix `an issue with Ansible Collections`__ where roles used via the
  ``include_role`` Ansible module broke due to the split into multiple
  collections. All roles will now have the ``debops.debops`` collection
  included by default in the :file:`meta/main.yml` file to tell Ansible where
  to look for dependent roles.

  .. __: https://github.com/ansible/ansible/issues/67723

- Fix an issue with the collection creation script where the role files that
  contained multiple uses of a particular custom Ansible plugin, for example
  ``template_src`` or ``file_src``, were modified multiple times by the script.

:ref:`debops.apt` role
''''''''''''''''''''''

- Fix BeagleBoards detection with Debian 10 image.
  Tested with a BeagleBoards Black.

:ref:`debops.cron` role
'''''''''''''''''''''''

- Fix creation of empty environment variables in :command:`cron` configuration
  files managed by Ansible.

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- :envvar:`dnsmasq__public_dns` did not create a firewall allow rule when no
  interfaces where specified.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- Fixed incorrect removal of the ferm rule set by :ref:`debops.avahi` on
  IPv6-enabled systems.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- Don't re-create removed :file:`/etc/machine-id` contents during Vagrant box
  creation. This should fix issues with IP addresses received from DHCP by the
  Vagrant machines.

  .. warning:: This fix is applied using the :command:`patch` command on the
               files packaged by APT. Existing installations will have to be
               updated manually, alternatively the changes applied previously
               should be removed from the affected files before the role is
               applied. See the patch files in the role :file:`files/patches/`
               directory for more information.

- The GitLab package repository signing key has been replaced with the new key
  that has been in use since 2020-04-06, allowing APT to update package lists
  again. See the `GitLab.com blog`__ for more information about this change.

  .. __: https://about.gitlab.com/releases/2020/03/30/gpg-key-for-gitlab-package-repositories-metadata-changing/

:ref:`debops.minio` role
''''''''''''''''''''''''

- Fix an issue during installation of recent MinIO releases, where during an
  initial restart the MinIO service would switch into "safe mode" when
  a problem with configuration is detected; this would prevent the service to
  be restarted correctly. Now the service should be properly stopped by
  :command:`systemd` after a stop timeout.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- Use short timeout for DNS queries performed by the Ansible local fact script,
  in case that the DNS infrastructure is not configured. This avoids 60s
  timeouts during Ansible fact gathering in such cases.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role now always sets the HTTP Strict Transport Security header when it is
  enabled, regardless of the response code.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- In the :command:`autopostgresqlbackup` script, use the
  :command:`su  - postgres` command instead of the :command:`su postgres`
  command to start a login shell and switch to the correct home directory of
  the ``postgres`` user instead of staying in the :file:`/root/` home
  directory.  This avoids the issue during execution of the script via
  :command:`cron` where it would emit errors about not being able to change to
  the :file:`/root/` home directory due to the permissions.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- Use the Roundcube version from Ansible local facts instead of the one defined
  in role default variables to detect if a database migration is required after
  Roundcube :command:`git` repository is updated.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Move the Private Enterprise Number and LDAP namespace OIDs of the DebOps
  organization to a separate :file:`debops.schema` file to avoid duplicated
  OIDs in the ``cn=schema`` LDAP subtree.

  Existing installations might need to be recreated to avoid warnings about
  duplicate OIDs emitted during OpenLDAP operations.


`debops v2.0.0`_ - 2020-01-30
-----------------------------

.. _debops v2.0.0: https://github.com/debops/debops/compare/v1.2.0...v2.0.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.lxd` role brings support for LXD on Debian hosts by building
  the Go binaries from source, without Snap installation.

General
'''''''

- The DebOps Python package now includes the ``debops.<role>(5)`` manual pages
  for most of the DebOps roles with  details about role usage, variable
  definition and the like. The manual pages are based on the existing role
  documentation.

- The DebOps project directories can now include the
  :file:`ansible/global-vars.yml` file which can be used to define :ref:`global
  Ansible variables <global_vars>` that can affect playbook initialization.

:ref:`debops.docker_registry` role
''''''''''''''''''''''''''''''''''

- The :envvar:`docker_registry__basic_auth_except_get` variable allows to setup
  a simple authentication schema without the need to deploy a fully blown
  Docker Registry Token Authentication.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Add `docker_server__install_virtualenv` setting to disable python virtualenv installation.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- The role can now use DNS SRV resource records to find the GitLab API host
  address. Additionally, GitLab Runner token can be stored in the
  :file:`secret/` directory in a predetermined location to avoid exposing it
  via the Ansible inventory. See the role documentation for details.

:ref:`debops.icinga` role
'''''''''''''''''''''''''

- The role now configures the Icinga REST API to also listen on IPv6 addresses.
  It is possible to change the listen address and port through the
  ``icinga__api_listen`` and ``icinga__api_port`` variables.

:ref:`debops.nslcd` role
''''''''''''''''''''''''

- The role will now use a LDAP host filter by default, to allow for easy
  control over what UNIX accounts and UNIX groups are present on which hosts
  using the ``host`` LDAP attribute.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- A given PostgreSQL server cluster can be configured to enable `standby
  replication mode`__, and receive streaming replication data from a master
  PostgreSQL server. See role documentation for examples.

  .. __: https://www.postgresql.org/docs/current/warm-standby.html

- The :command:`autopostgresqlbackup` script can be configured to tell the
  :command:`pg_dump` command to compress the generated backup files on the fly
  instead of creating a separate ``.sql`` file and compressing it afterwards.
  This mode is currently disabled by default.

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- The role can now define static DNS configuration to be merged with other DNS
  data sources in the :file:`/etc/resolv.conf` configuration file.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- The Roundcube installation is now more integrated with the DebOps
  environment. The role will automatically configure :ref:`Redis
  <debops.redis_server>` and :ref:`memcached <debops.memcached>` support if
  they are detected on the Roundcube host, which should improve application
  performance.

- If LDAP infrastructure is detected on the host, Roundcube will be configured
  to use the LDAP directory managed by DebOps as an address book.

- The ManageSieve Roundcube plugin will be enabled by default to allow
  configuration of Sieve filter scripts. The role will use the DNS SRV resource
  records to find the Sieve service host and port to use.

- The role can now use PostgreSQL as a database backend. The database server
  can be managed with the :ref:`debops.postgresql_server` role.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The :ref:`mailservice <slapd__ref_mailservice>` LDAP schema has been added to
  the :ref:`debops.slapd` role. It provides a set of object classes and
  attributes useful for defining e-mail recipients and simple mail distribution
  lists in the LDAP directory.

Changed
~~~~~~~

General
'''''''

- Reorder :file:`bootstrap.yml` Ansible playbook to also work for systems freshly
  installed from CD. :ref:`debops.apt` needs to be run early to regenerate
  :file:`/etc/apt/sources.list` which might still contain a now not functional
  CD entry.

- Most of the role dependencies have been moved either to the playbooks or to
  the role task lists using the ``import_role`` Ansible module.

- The official DebOps roles have been renamed and the ``debops.`` prefix has
  been dropped from the directory names to better support Ansible Collections.
  Custom playbooks and role dependencies which use the DebOps roles have to be
  updated to work again.

- The :file:`<role_name>/env` "sub-roles" in various DebOps roles have been
  redesigned for use via the ``import_role`` Ansible module to improve support
  for Ansible Collections. Existing Ansible playbooks that use such "sub-roles"
  will have to be updated; check the playbooks included in DebOps for the new
  usage examples.

- The ``collections:`` keyword was added in all DebOps playbooks to support
  usage with roles, modules and other plugins in an Ansible Collection. Due to
  this, Ansible 2.8+ is required to use DebOps playbooks.

- The paths to the passwords stored in the :file:`secret/` directory by various
  roles have been changed to use the ``inventory_hostname`` variable instead of
  the ``ansible_fqdn`` variable. This change will result in passwords set in
  various services to be regenerated, which might have an impact on service
  availability. See :ref:`upgrade_notes` for details.

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- The RoundCube version installed by the :ref:`debops.roundcube` role has been
  updated to the `1.4.1 release`__, which includes a new "Elastic" theme
  compatible with mobile devices, and other improvements.

  .. __: https://github.com/roundcube/roundcubemail/releases/tag/1.4.1

- The Nextcloud version installed by the :ref:`debops.owncloud` role is updated
  to Nextcloud 16.0 release. The ownCloud version has been updated to 10.3.

- The Icinga Director version installed by the :ref:`debops.icinga_web` role
  has been updated to the v1.7.2 release. Notable changes in `v1.7.x`__ are new
  German and Japanese translations, side-by-side sync previews, a new
  background daemon to replace the job runner and new module dependencies.
  Other Icinga Web modules have also been updated to their latest versions.

  .. __: https://github.com/Icinga/icingaweb2-module-director/releases/tag/v1.7.0

LDAP
''''

- The ``authorizedService`` and ``host`` LDAP attribute values used for access
  control in various DebOps roles and the :file:`ldap/init-directory.yml`
  playbook have been updated and made consistent with the
  :ref:`ldap__ref_ldap_access` documentation. You need to update the LDAP
  entries that use them before applying these changes on the hosts managed by
  DebOps. See :ref:`upgrade_notes` for detailed list of changed values.

Mail Transport Agents
'''''''''''''''''''''

- The :envvar:`nullmailer__mailname` and the :envvar:`postfix__mailname`
  variables will use the host's FQDN address instead of the DNS domain as the
  mailname. This was done to not include the hostnames in the e-mail addresses,
  however this is better handled by Postfix domain masquerading done on the
  mail relay host, which allows for exceptions, supports multiple DNS domains
  and does not break mail delivery in subtle ways. See the
  :ref:`debops.nullmailer` role documentation for an example configuration.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Replace the deprecated `docker_server__graph` variable with the
  ``docker_server__data_root`` variable.

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- The role gained support for mail accounts stored in the LDAP directory, based
  on the :ref:`DebOps LDAP infrastructure <debops.ldap>`. When the LDAP
  environment is detected on the host, the LDAP support will be enabled
  automatically, and mail accounts based on POSIX accounts will be disabled.

- The default mailbox format used by Dovecot has been changed from ``mbox`` to
  Maildir; the user mailboxes will be stored by default in the
  :file:`~/Maildir/` subdirectory of a given user account. On existing
  installations, the mailboxes might need to be converted and moved manually.

- Dovecot will use the host DNS domain as the default SASL realm when users
  will not specify their domain in their login username.

- The role should better integrate with the :ref:`DebOps PKI environment
  <debops.pki>` and gracefully disable TLS support when it has not been
  configured.

- The firewall configuration has been redesigned and the :ref:`debops.dovecot`
  role no longer generates the :command:`ferm` configuration files directly,
  instead using the :ref:`debops.ferm` role as a dependency.

- Add option to enable ManageSieve by default without the need to update the config_maps,
  to allow configuration of Sieve filter scripts.

- Restored :envvar:`dovecot__mail_location` to original value of `maildir:~/Maildir`. It was
  wrongfully changed to `/var/vmail/%d/%n/mailbox` if LDAP was enabled. See also
  :envvar:`dovecot__vmail_home`.

- If the LDAP support is enabled, the role will no longer configure Postfix via
  the :ref:`debops.postfix` role to deliver local mail via Dovecot LMTP
  service; this breaks mail delivery to local UNIX accounts (for example
  ``root``) which might not have corresponding aliases in the virtual mail
  database. Instead, ``virtual_transport`` option will be configured to pass
  mail via LMTP to Dovecot, which then will deliver it to the virtual mailboxes
  in :file:`/var/vmail/` subdirectories.

:ref:`debops.icinga_web` role
'''''''''''''''''''''''''''''

- The ``icinga2-director-jobs.service`` systemd service has been replaced with
  ``icinga-director.service``. This service manages a new daemon that is
  required for Icinga Director v1.7.0+.

:ref:`debops.memcached` role
''''''''''''''''''''''''''''

- All variables in the role have been renamed from ``memcached_*`` to
  ``memcached__*`` to create the role namespace. You need to update the
  inventory accordingly.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- The upstream SMTP relay will be detected automatically using DNS SRV resource
  records, if they are defined.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Drop Nextcloud 15 support because it is EOL. You need to upgrade Nextcloud
  manually if you are running version 15 or below. The role now defaults to
  Nextcloud 16 for new installations.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- If both :ref:`Dovecot <debops.dovecot>` and :ref:`Cyrus <debops.saslauthd>`
  services are installed on a host, Postfix will be configured to prefer Cyrus
  for SASL authentication. This permits mail relay via the authenticated
  :ref:`nullmailer <debops.nullmailer>` Mail Transfer Agents with accounts in
  the LDAP directory. The preference can be changed using the
  :envvar:`postconf__sasl_auth_method` variable.

:ref:`debops.roundcube` role
''''''''''''''''''''''''''''

- The variable that defines the FQDN address of the RoundCube installation has
  been changed from :envvar:`roundcube__domain` to :envvar:`roundcube__fqdn`.
  The default subdomain has also been changed from ``roundcube`` to ``webmail``
  to offer a more widely used name for the application.

- The default RoundCube installation path defined in the
  :envvar:`roundcube__git_dest` variable has been changed and no longer
  uses the web application FQDN. This should make changing the web application
  address independent from the installation directory.

  Due to this change, existing installations will be re-installed in the new
  deployment path. Checking the changes in a development environment is
  recommended before deploying them in production environment.

- The role will use DNS SRV resource records to find the IMAP and/or SMTP
  (submission) services to use in the RoundCube Webmail configuration, with
  a fallback to static subdomains. See :ref:`roundcube__ref_srv_records` for
  more details.

- RoundCube will use the user login and password credentials to authenticate to
  the SMTP (submission) service before sending e-mail messages. This allows the
  SMTP server to check the message details, block mail with forged sender
  address, etc. The default configuration uses encrypted connections to the
  IMAP and SMTP services to ensure confidentiality and security.

- User logins that don't specify a domain will have the host domain
  automatically appended to them during authentication. This solves an issue
  where use of logins with or without domain for authentication would result in
  separate RoundCube profiles created in the database.

- The Roundcube configuration has been redesigned and now uses the custom
  Ansible filter plugins to generate the :file:`config/config.inc.php`
  configuration file. The format of the configuration variables has been
  changed, you will need to update the Ansible inventory.
  See :ref:`roundcube__ref_configuration` for more details.

- Roundcube installation tasks have been cleaned up and the old method of
  keeping track of the :command:`git` checkout is replaced by new functionality
  of the ``git`` Ansible module. This requires full reinstallation of Roundcube
  application; see :ref:`upgrade_notes` for more details.

- Support for Roundcube plugins has been redesigned and now uses custom Ansible
  filters included in DebOps to manage plugins. The role can install plugins
  from the Roundcube plugin repository and manage their configuration files.
  A :envvar:`set of default plugins <roundcube__default_plugins>` has been
  defined to make the default Roundcube installation a bit more user-friendly.

:ref:`debops.ntp` role
''''''''''''''''''''''

- Chrony will not listen on udp control port on loopback anymore. Unix sockets
  are a better way for chronyc to talk to chronyd where local access is
  controlled by file permissions. This is suggested in the Chrony FAQ "How can
  I make chronyd more secure?".

- Chrony: Support :envvar:`ntp__listen` value ``*`` to make transitioning away
  from ``ntpd`` easier.

- Chrony: Reduce default NTP servers considered as time source from 4 pool addresses
  (from which Chrony used 4 NTP servers each – 16 in total) to just 1 pool
  address – 4 NTP time sources in total.


Removed
~~~~~~~

General
'''''''

- Old ``[debops_<role_name>]`` Ansible inventory groups have been removed from
  DebOps playbooks. Users should use the ``[debops_service_<role_name>]``
  group names instead.

Fixed
~~~~~

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Do not add empty entries from `docker_server__listen` to daemon.json.
  This causes the docker daemon to not parse the config and crash.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The ``dmz`` firewall configuration will now not interpret the port as part of
  a IPv6 address anymore. We now protect the IPv6 address by surrounding it by
  ``[]``.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- Fix issue with GitLab Runner failing test jobs due to the default
  :file:`~/.bash_logout` script wiping the terminal on logout. The role will
  skip copying the :file:`/etc/skel/` contents on the new installations;
  existing script will be removed.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- Again, redirect the e-mail messages for local recipients to the central
  ``root`` e-mail account (but local to the SMTP relay). This fixes an issue
  where e-mail messages were left in the mail queue and filled the disk space.

:ref:`debops.php` role
''''''''''''''''''''''

- Change the default list of preferred PHP versions to include PHP 7.3 as the
  preferred version. This should ensure that on hosts with the Ondřej Surý PHP
  repositories enabled, PHP 7.3 will be installed by default even though newer
  versions are available. This should solve installation issues with many PHP
  applications that don't have full support for PHP 7.4+ release yet.


`debops v1.2.0`_ - 2019-12-01
-----------------------------

.. _debops v1.2.0: https://github.com/debops/debops/compare/v1.1.0...v1.2.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- Add :ref:`debops.postldap` Ansible role to configure and enable
  :ref:`debops.postfix` to host multiple (virtual) domains,and thus provide
  email service to several domains with just one `mail server`.
  Currently the Virtual Mail support works only with **LDAP enabled**,
  in the future `mariaDB` could be enabled.

- The :ref:`debops.minio` and :ref:`debops.mcli` Ansible roles can be used to
  install and configure `MinIO`__ object storage service and its corresponding
  client binary.

  .. __: https://minio.io/

- The :ref:`debops.tinyproxy` role can be used to set up a lightweight
  HTTP/HTTPS proxy for an upstream server.

- The :ref:`debops.libuser` Ansible role configures the `libuser`__ library and
  related commands. This library is used by some of the other DebOps roles to
  manage local UNIX accounts and groups on LDAP-enabled hosts.

  .. __: https://pagure.io/libuser/

General
'''''''

- Add more entries to be ignored by default by the :command:`git` command in
  the DebOps project directories:

  - :file:`debops`: ignore DebOps monorepo cloned or symlinked into the project
    directory.

  - :file:`roles` and :file:`playbooks`: ignore roles and playbooks in
    development; production code should be put in the :file:`ansible/roles/`
    and the :file:`ansible/playbooks/` directories respectively.

- The :command:`debops-init` script now also creates the .gitattributes file
  for use with :command:`git-crypt`. It is commented out by default.

- The :command:`debops-defaults` command will check what pagers
  (:command:`view`, :command:`less`, :command:`more`) are available and use the
  best one automatically.

- A new Ansible module, ``dpkg_divert``, can be used to divert the
  configuration files out of the way to preserve them and avoid issues with
  package upgrades. The module is available in the
  :ref:`debops.ansible_plugins` role.

LDAP
''''

- The :file:`ldap/init-directory.yml` Ansible playbook will create the LDAP
  objects ``cn=LDAP Replicators`` and ``cn=Password Reset Agents`` to allow
  other Ansible roles to utilize them without the need for the system
  administrator to define them by hand.

- The :file:`ldap/get-uuid.yml` Ansible playbook can be used to convert LDAP
  Distinguished Names to UUIDs to look up the password files if needed.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The `open-vm-tools`__ APT package will be installed by default in VMware
  virtual machines.

  .. __: https://github.com/vmware/open-vm-tools

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- The role will tell the client applications to `disable DNS-over-HTTPS
  support`__ using the ``use-application-dns.net`` DNS record. This should
  allow connections to internal sites and preserve the split-DNS functionality.

  .. __: https://support.mozilla.org/en-US/kb/canary-domain-use-application-dnsnet

:ref:`debops.dokuwiki` role
'''''''''''''''''''''''''''

- The role will configure LDAP support in DokuWiki when LDAP environment
  managed by the :ref:`debops.ldap` Ansible role is detected. Read the
  :ref:`dokuwiki__ref_ldap_support` chapter in the documentation for more
  details.

:ref:`debops.cron` role
'''''''''''''''''''''''

- The execution time of the ``hourly``, ``daily``, ``weekly`` and ``monthly``
  :command:`cron` jobs will be randomized on a per-host basis to avoid large
  job execution spikes every morning. See the role documentation for more
  details.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- When the :ref:`LDAP environment <debops.ldap>` is configured on a host, the
  :ref:`debops.nullmailer` role will create the service account in the LDAP
  directory and configure the :command:`nullmailer` service to use SASL
  authentication with its LDAP credentials to send e-mails to the relayhost.

:ref:`debops.pki` role
''''''''''''''''''''''

- Newly created PKI realms will have a new :file:`public/full.pem` file which
  contains the full X.509 certificate chain, including the Root CA certificate,
  which might be required by some applications that rely on TLS.

  Existing PKI realms will not be modified, but Ansible roles that use the PKI
  infrastructure might expect the new files to be present. It is advisable to
  :ref:`recreate the PKI realms <pki__ref_realm_renewal>` when possible, or
  create the missing files manually.

:ref:`debops.saslauthd` role
''''''''''''''''''''''''''''

- The role can now be used to authenticate users of different services against
  the LDAP directory via integration with the :ref:`debops.ldap` role and its
  framework. Multiple LDAP profiles can be used to provide different access
  control for different services.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Add support for :ref:`eduPerson LDAP schema <slapd__ref_eduperson>` with
  updated schema file included in the role.

- The role will configure SASL authentication in the OpenLDAP service using the
  :ref:`debops.saslauthd` Ansible role. Both humans and machines can
  authenticate to the OpenLDAP directory using their respective LDAP objects.

- The :ref:`lastbind overlay <slapd__ref_lastbind_overlay>` will be enabled by
  default. This overlay records the timestamp of the last successful bind
  operation of a given LDAP object, which can be used to, for example, check
  the date of the last successful login of a given user account.

- Add support for :ref:`nextcloud LDAP schema <slapd__ref_nextcloud>` which
  provides attributes needed to define disk quotas for Nextcloud user accounts.

- The Access Control List rules can now be tested using the :man:`slapacl(8)`
  command via a generated :ref:`test suite script <slapd__ref_acl_tests>`.

- The default ACL rules have been overhauled to add support for the
  ``ou=Roles,dc=example,dc=org`` subtree and use of the ``organizationalRole``
  LDAP objects for authorization. The old set of rules is still active to
  ensure that the existing environments work as expected.

  If you use a modified ACL configuration, you should include the new rules as
  well to ensure that changes in the :ref:`debops.ldap` support are working
  correctly.

- You can now hide specific LDAP objects from unprivileged users by adding them
  to a special ``cn=Hidden Objects,ou=Groups,dc=example,dc=org`` LDAP group.
  The required ACL rule will be enabled by default; the objects used to control
  visibility will be created by the :file:`ldap/init-directory.yml` playbook.

- New "SMS Gateway" LDAP role grants read-only access to the ``mobile``
  attribute by SMS gateways. This is needed for implementing 2-factor
  authentication via SMS messages.

:ref:`debops.unbound` role
''''''''''''''''''''''''''

- The role will tell the client applications to `disable DNS-over-HTTPS
  support`__ using the ``use-application-dns.net`` DNS record. This should
  allow connections to internal sites and preserve the split-DNS functionality.

  .. __: https://support.mozilla.org/en-US/kb/canary-domain-use-application-dnsnet

- The role will configure the :command:`unbound` daemon to allow non-recursive
  access to DNS queries when a host is managed by Ansible locally, with
  assumption that it's an Ansible Controller host. This change unblocks use of
  the :command:`dig +trace` and similar commands.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.gitlab` role, GitLab version has been updated to
  ``12.2``. This is the last release that supports Ruby 2.5 which is included
  in Debian Buster.

- In the :ref:`debops.ipxe` role, the Debian Stretch and Debian Buster netboot
  installer versions have been updated to their next point releases, 9.10 and
  10.2 respectively.

- In the :ref:`debops.netbox` role, the NetBox version has been updated to
  ``v2.6.3``.

Continuous Integration
''''''''''''''''''''''

- The ``$DEBOPS_FROM`` environment variable can be used to select how DebOps
  scripts should be installed in the Vagrant environment: either ``devel``
  (local build) or ``pypi`` (installation from PyPI repository). This makes
  Vagrant environment more useful on Windows hosts, where :file:`/vagrant`
  directory is not mounted due to issues with symlinks.

- The :command:`make test` command will not run the Docker tests anymore, to
  make the default tests faster. To run the Docker tests with all other tests,
  you can use the :command:`make test docker` command.

General
'''''''

- External commands used in the DebOps scripts have been defined as constants
  to allow easier changes of the command location in various operating systems,
  for example Guix.

- The default Ansible callback plugin used by DebOps is changed to ``yaml``,
  which gives a cleaner look for various outputs and error messages. The
  callback plugin will be active by default in new DebOps project directories;
  in existing directories users can add:

  .. code-block:: ini

     [ansible defaults]
     stdout_callback = yaml

  in the :file:`.debops.cfg` configuration file.

LDAP
''''

- The :file:`ldap/init-directory.yml` playbook has been updated to use the new
  ``ou=Roles,dc=example,dc=org`` LDAP subtree, which will contain various
  ``organizationalRole`` objects. After updating the OpenLDAP Access Control
  List using the :ref:`debops.slapd` role, you can use the playbook on an
  existing installation to create the missing objects.

  The ``cn=UNIX Administrators`` and ``cn=UNIX SSH users`` LDAP objects will be
  created in the ``ou=Groups,dc=example,dc=org`` LDAP subtree. On existing
  installations, these objects need to be moved manually to the new subtree,
  otherwise the playbook will try to create them and fail due to duplicate
  UID/GID numbers which are enforced to be unique. You can move the objects
  using an LDAP client, for example Apache Directory Studio.

  The ``ou=System Groups,dc=example=dc,org`` subtree will not be created
  anymore. On existing installations this subtree will be left intact and can
  be safely removed after migration.

- The access to the OpenLDAP service configured using the :ref:`debops.slapd`
  role now requires explicit firewall and TCP Wrappers configuration to allow
  access from trusted IP addresses and subnets. You can use the
  ``slapd__*_allow`` variables in the Ansible inventory to specify the IP
  addresses and subnets that can access the service.

  To preserve the old behaviour of granting access by default from anywhere,
  you can set the :envvar:`slapd__accept_any` variable to ``True``.

:ref:`debops.apt_preferences` role
''''''''''''''''''''''''''''''''''

- Support Debian Buster in :ref:`apt_preferences__list`.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The LDAP support in GitLab has been converted to use the
  :ref:`debops.ldap` infrastructure and not configure LDAP objects directly.
  LDAP support in GitLab will be enabled automatically if it's enabled on
  the host. Some of the configuration variables have been changed; see the
  :ref:`upgrade_notes` for more details.

- The default LDAP filter configured in the
  :envvar:`gitlab__ldap_user_filter` variable has been modified to limit
  access to the service to objects with specific attributes. See the
  :ref:`GitLab LDAP access control <gitlab__ref_ldap_dit_access>`
  documentation page for details about the required attributes and their
  values.

- The GitLab project has changed its codebase structure, because of that the
  Gitlab CE :command:`git` repository has been moved to a new location,
  https://gitlab.com/gitlab-org/gitlab-foss/. The role has been updated
  accordingly. Existing installations should work fine after the new codebase
  is cloned, but if unsure, users should check the change first in
  a development environment.

  More details can be found in GitLab blog posts `here`__ and `here`__, as well
  as the `Frequently Asked Questions`__ page.

  .. __: https://about.gitlab.com/blog/2019/02/21/merging-ce-and-ee-codebases/
  .. __: https://about.gitlab.com/blog/2019/08/23/a-single-codebase-for-gitlab-community-and-enterprise-edition/
  .. __: https://gitlab.com/gitlab-org/gitlab/issues/13855

:ref:`debops.golang` role
'''''''''''''''''''''''''

- The role has been redesigned from the ground up, and can be used to install
  Go applications either from APT packages, build them from source, or download
  precompiled binaries from remote resources. See the role documentation for
  more details.

:ref:`debops.ldap` role
'''''''''''''''''''''''

- The role will reset the LDAP host attributes defined in the
  :envvar:`ldap__device_attributes` variable on first configuration in case
  that the host has been reinstalled and some of their values changed (for
  example different IP addresses). This should avoid leaving the outdated
  attributes in the host LDAP object.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role will create the webroot directory specified in the ``item.root``
  parameter even if the ``item.owner`` and ``item.group`` parameters are not
  defined. This might have idempotency issues if the :ref:`debops.nginx` role
  configuration and the application role configuration try to modify the same
  directory attributes. To disable the webroot creation, you can set the
  ``item.webroot_create`` parameter to ``False``. Alternatively, you should
  specify the intended owner, group and directory mode in the :command:`nginx`
  server configuration.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- The :envvar:`nullmailer__adminaddr` list is set to empty by default to not
  redirect all e-mail messages sent through the :command:`nullmailer` service
  to the ``root`` account. This should be done on the relayhost instead.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Drop Nextcloud 14 support because it is EOL. You need to upgrade Nextcloud
  manually if you are running 14 or below. Add Nextcloud 16 support. Now
  default to Nextcloud 15 for new installations.

- The LDAP support in Nextcloud has been converted to use the
  :ref:`debops.ldap` infrastructure and not configure LDAP objects directly.
  LDAP support in Nextcloud will be enabled automatically if it's enabled on
  the host. Some of the configuration variables have been changed; see the
  :ref:`upgrade_notes` for more details.

- The default LDAP filter configured in the
  :envvar:`owncloud__ldap_login_filter` variable has been modified to limit
  access to the service to objects with specific attributes. See the
  :ref:`Nextcloud LDAP access control <owncloud__ref_ldap_dit_access>`
  documentation page for details about the required attributes and their
  values.

- The default LDAP group filter configured in the
  :envvar:`owncloud__ldap_group_filter` variable has been modified to limit the
  available set of ``groupOfNames`` LDAP objects to only those that have the
  ``nextcloudEnabled`` attribute set to ``true``.

- Support for disk quotas for LDAP users has been added in the default
  configuration, based on the :ref:`nextcloud LDAP schema
  <slapd__ref_nextcloud>`. The default disk quota is set to 10 GB and can be
  changed using the ``nextcloudQuota`` LDAP attribute.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- Support for the ``465`` TCP port for message submission over Implicit TLS is
  no longer deprecated (status changed by the :rfc:`8314` document) and will be
  enabled by default with the ``auth`` capability.

- The role will configure Postfix to check the sender address of authenticated
  mail messages and block those that don't belong to the authenticated user.
  This will be enabled with the ``auth`` and the ``unauth-sender``
  capabilities, and requires an user database to work correctly.

:ref:`debops.postfix` role
''''''''''''''''''''''''''

- The default primary group of the lookup tables has been changed to
  ``postfix``, default mode for new lookup tables will be set to ``0640``.
  This change helps secure lookup tables that utilize remote databases with
  authentication.

- Postfix lookup tables can now use shared connection configuration defined in
  a YAML dictionary to minimize data duplication.
  See the :ref:`postfix__ref_lookup_tables` documentation for more details.

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- The role will install and configure :command:`resolvconf` APT package only on
  hosts with more than one network interface (not counting ``lo``), or if local
  DNS services are also present on the host.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Enable substring index for the ``sudoUser`` attribute from the :ref:`sudo
  LDAP schema <slapd__ref_sudo>`. Existing installations should be updated
  manually via the LDAP client, by setting the value of the ``sudoUser`` index
  to ``eq,sub``.

- Add indexes for the ``authorizedService`` and ``host`` attributes from the
  :ref:`ldapns LDAP schema <slapd__ref_ldapns>` and the ``gid`` attribute from
  the :ref:`posixGroupId LDAP schema <slapd__ref_posixgroupid>`. This should
  improve performance in UNIX environments connected to the LDAP directory.

- The number of rounds in SHA-512 password hashes has been increased from 5000
  (default) to 100001. Existing password hashes will be unaffected.

- The ``employeeNumber`` attribute in the ``ou=People,dc=example,dc=org`` LDAP
  subtree will be constrained to digits only, and the LDAP directory will
  enforce its uniqueness in the subtree. This allows the attribute to be used
  for correlation of personal LDAP objects to RDBMS-based databases.

- The ``mail`` attribute is changed from unique for objects in the
  ``ou=People,dc=example,dc=org`` LDAP subtree to globally unique, due to its
  use for authentication purposes. The attribute will be indexed by default.

- Access to the ``carLicense``, ``homePhone`` and ``homePostalAddress``
  attributes has been restricted to privileged accounts only (administrators,
  entry owner). The values cannot be seen by unprivileged and anonymous users.

- Write access to the ``ou=SUDOers,dc=example,dc=org`` LDAP subtree has been
  restricted to the members of the "UNIX Administrators" LDAP group.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The role will allow or deny access to the ``root`` account via password
  depending on the presence of the :file:`/root/.ssh/authorized_keys` file. See
  :ref:`sshd__ref_root_password` for more details. This requires updated
  :file:`root_account.fact` script from the :ref:`debops.root_account` role.

- The role will use Ansible local facts to check if OpenSSH server package is
  installed to conditionally enable/disable its start on first install.

debops-contrib.dropbear_initramfs role
''''''''''''''''''''''''''''''''''''''

- Better default value for `dropbear_initramfs__network_device` by
  detecting the default network interface using Ansible facts instead of the
  previously hard-coded ``eth0``.

Removed
~~~~~~~

:ref:`debops.ansible_plugins` role
''''''''''''''''''''''''''''''''''

- The ``ldappassword`` Ansible filter plugin has been removed as it is no
  longer used in DebOps roles. The preferred method for storing passwords in
  LDAP is to pass them in plaintext (over TLS) and let the directory server
  store them in a hashed form. See also: :rfc:`3062`.

:ref:`debops.ldap` role
'''''''''''''''''''''''

- The use of the ``params`` option in the ``ldap_attrs`` and ``ldap_entry``
  Ansible modules is deprecated due to their insecure nature. As a consequence,
  the :ref:`debops.ldap` role has been updated to not use this option and the
  ``ldap__admin_auth_params`` variable has been removed.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Set `nginx_upstream_php5_www_data` to absent. If you are still using
  that Nginx upstream which was enabled by default then update your Ansible
  role and switch to a supported PHP release.

Fixed
~~~~~

General
'''''''

- The "Edit on GitHub" links on the role default variable pages in the
  documentation have been fixed and now point to the correct source files on
  GitHub.

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- On Ubuntu hosts, the role will fix the configuration installed by the
  :command:`lxd` package to use ``bind-dynamic`` option instead of
  ``bind-interfaces``. This allows the :command:`dnsmasq` service to start
  correctly.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The ``dmz`` firewall configuration will use the ``dport`` parameter instead
  of ``port``, otherwise filtering rules will not work as expected.

:ref:`debops.nfs_server` role
'''''''''''''''''''''''''''''

- In the :envvar:`nfs_server__firewall_ports` variable, convert the
  ``dict_keys`` view into a list due to `change in Python 3 implementation`__
  of dictionaries.

  .. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_python_version.html#dictionary-views

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Fix an issue in the :file:`php.conf.j2` server template when an
  ``item.location`` parameter is specified, overriding the default set of
  ``location`` blocks defined in the :file:`default.conf.j` template. If the
  ``/`` location is not specified in the ``item.location`` dictionary,
  a default one will be included by the role.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- Disable the ``smtpd_helo_restrictions`` option on the ``submission`` and
  ``smtps`` TCP ports when the authentication and MX lookups are enabled. This
  should fix an issue where SMTP client sends the host's IP address as its
  HELO/EHLO response, which might not be configurable by the user.

Security
~~~~~~~~

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Mitigation for the `CVE-2019-11043`__ vulnerability has been applied in the
  :command:`nginx` ``php`` and ``php5`` configuration templates. The mitigation
  is based on the `suggested workaround`__ from the PHP Bug Tracker.

  .. __: https://security-tracker.debian.org/tracker/CVE-2019-11043
  .. __: https://bugs.php.net/bug.php?id=78599

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Security patch for the `CVE-2019-11043`__ vulnerability has been applied in
  the Nextcloud configuration for the :ref:`debops.nginx` role. The patch is
  based on the `fix suggested by upstream`__.

  .. __: https://security-tracker.debian.org/tracker/CVE-2019-11043
  .. __: https://nextcloud.com/blog/urgent-security-issue-in-nginx-php-fpm/


`debops v1.1.0`_ - 2019-08-25
-----------------------------

.. _debops v1.1.0: https://github.com/debops/debops/compare/v1.0.0...v1.1.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.keyring` role is designed to be used by other Ansible roles to
  manage the GPG keys, either in the APT keyring or the GPG keyrings of
  specific UNIX accounts. It replaces and centralizes the use of the
  ``apt_key`` and the ``apt_repository`` Ansible modules in separate roles
  and provides additional functionality, like GPG key lookup in a local key
  store on the Ansible Controller, or the `Keybase`__ service.

  .. __: https://keybase.io/

- The ``debops-contrib.neurodebian`` Ansible role has been migrated to the
  main DebOps role namespace as the :ref:`debops.neurodebian` role. This role
  can be used to configure the `NeuroDebian`__ APT repository on
  Debian/Ubuntu hosts.

  .. __: http://neuro.debian.net/

- The :ref:`debops.wpcli` role can be used to install the WP-CLI framework to
  allow management of WordPress websites in a shared hosting environment.

- The :ref:`debops.nscd` role configures the Name Service Cache Daemon, used to
  cache NSS entries from remote databases, for example LDAP, Active Directory
  or NIS. The role is included in the :file:`bootstrap-ldap.yml` playbook.

- The :ref:`debops.backup2l` role configures the `backup2l`__ script which can
  create differential backups of a given host and store them on an external
  hard drive connected to that host.

  .. __: https://gkiefer.github.io/backup2l/

- The :ref:`debops.resolvconf` role fixes a few issues in the ``resolvconf``
  Debian package and modifies the interface order in the generated
  :file:`/etc/resolv.conf` configuration file depending on presence of a local
  DNS resolver like ``dnsmasq`` or ``unbound``. The role is included in the
  bootstrap and common playbooks.

Continuous Integration
''''''''''''''''''''''

- The Vagrant test environment will use the `libeatmydata`__ library to make
  specific commands like :command:`apt-get`, :command:`rsync`, :command:`pip`,
  etc. faster by avoiding excessive :man:`fsync(2)` operations.

  .. __: https://www.flamingspork.com/projects/libeatmydata/

General
'''''''

- The ``pyopenssl`` Python package has been added as a dependency of DebOps
  when the project is installed with Ansible included. This package is required
  by the ``openssl_*`` modules in Ansible 2.7; some of the DebOps roles like
  :ref:`debops.opendkim` use these modules on the Ansible Controller.

- The ``distro`` Python package has been added as the DebOps dependency. The
  package is used by the :command:`debops-init` script to detect the operating
  system used on the Ansible Controller, and is a replacement for the
  deprecated ``platform.linux_distribution()`` function.

LDAP
''''

- The :file:`ldap/init-directory.yml` Ansible playbook will create an LDAP
  group object for SSH users, equivalent to the ``sshusers`` group created by
  the :ref:`debops.system_groups` role. LDAP accounts in this group will be
  able to access SSH service from any host. Existing installations might need
  to be updated manually to fix UID/GID or LDAP DN conflicts.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- If Avahi/mDNS support is present on a host, the :ref:`debops.ferm` role will
  allow access through the ``mdns`` UDP port by default. This will most likely
  happen on workstations and laptops with full desktop environments installed,
  but not on servers with minimal install. To configure Avahi service or enable
  it on servers, you can use the :ref:`debops.avahi` Ansible role.

:ref:`debops.libvirtd` role
'''''''''''''''''''''''''''

- The role will configure the ``libvirt`` and ``libvirt_guest`` NSS modules in
  :file:`/etc/nsswitch.conf` database using the :ref:`debops.nsswitch` role to
  allow accessing the virtual machines or containers via their hostnames on the
  virtual machine host.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The :command:`lxc-prepare-ssh` script can now look up the SSH keys of the
  current user in LDAP if support for it is enabled on the LXC host.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Add support to disable logging per Nginx server.

- If a :command:`nginx` server configuration uses a domain with ``lxc.``
  prefix, for example inside of an internal LXC container, the role will
  include a redirect from ``host.lxc`` "virtual" domain to the real
  ``host.lxc.example.org`` domain. This ensures that HTTP requests to the
  ``http://host.lxc/`` URLs are redirected to the real LXC container hosts,
  depending on the DNS records and the HTTP client's resolver configuration.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The role can now control on which ports and services OpenLDAP listens for
  connections. The ``ldaps:///`` service is enabled by default when support for
  the :ref:`debops.pki` role is enabled on the OpenLDAP host.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The kernel protection for symlinks and hardlinks will be enabled by default
  on Debian/Ubuntu hosts.

- Don't use special configuration for containers to determine what kernel
  parameters can be modified. The role will rely on its own Ansible local facts
  for that.

:ref:`debops.unbound` role
''''''''''''''''''''''''''

- The :command:`unbound` service will be configured to forward ``*.lxc.{{
  ansible_domain }}`` DNS queries to the :command:`dnsmasq` service managed by
  the :ref:`debops.lxc` role (``lxc-net``), if LXC configuration is detected
  via local Ansible facts. The ``*.consul`` DNS queries will be forwarded to
  the :command:`consul` service, if its Ansible facts are detected.

:ref:`debops.users` role
''''''''''''''''''''''''

- Read :envvar:`users__default_shell` which was removed in `debops v1.0.0`_.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- The :ref:`debops.netbox` role has been updated to NetBox version ``v2.6.1``.
  Redis service is now required for NetBox; it can be installed separately via
  the :ref:`debops.redis_server` Ansible role.

  The NetBox version installed by DebOps has been changed from using the
  ``master`` branch, to specific tags, with the latest release (``v2.6.1``) set
  by default. The :command:`git` commit signature in the NetBox repository is
  also verified using the GitHub GPG key when the repository is cloned.

- In the :ref:`debops.cran` role, the upstream APT repository suite for CRAN
  has been updated to ``<release>-cran35/`` due to changes in APT repository
  structure.  Existing APT repository URLs might need to be removed manually
  from :file:`/etc/apt/sources.lists.d/` directory to make the APT service work
  as expected.

- The :ref:`debops.nodejs` role will now install NodeJS, NPM and Yarn packages
  from the OS release repository by default. On the Debian Oldstable release,
  the packages backported from the Debian Stable release will be used by
  default.  Installation of upstream NodeJS and NPM can be enabled using the
  :envvar:`nodejs__node_upstream` variable. Upstream Yarn can be enabled using
  the :envvar:`nodejs__yarn_upstream` variable.

  If the NodeJS upstream support is enabled, the NodeJS 8.x version will be
  installed on older Debian/Ubuntu releases, for example Debian Stretch and
  Ubuntu Bionic. Debian Buster and newer releases will use NodeJS 10.x
  version, to keep the Node version from upstream in sync with the one
  available in the OS repositories.

- In the :ref:`debops.etherpad` role, the default version installed by the role
  is changed from the ``develop`` branch to the ``v1.7.0`` version on older OS
  releases, and the ``v1.7.5`` version on Debian Buster and newer, to not force
  installation of the upstream NPM package by default.

Continuous Integration
''''''''''''''''''''''

- DebOps now uses ``xenial`` as the default OS release used in Travis-CI tests.
  The ``xenial`` images on Travis use the :command:`shellcheck` v0.6.0 to test
  shell scripts; if you want to run the :command:`test shell` command locally
  to check the script syntax, you will need to update your
  :command:`shellcheck` installation to the v0.6.0 version to match the one on
  Travis-CI. This version is at present not available in Debian, therefore
  a custom install will be needed. See the `ShellCheck install instructions`__
  for your preferred method.

  .. __: https://github.com/koalaman/shellcheck#installing-a-pre-compiled-binary

- The Travis-CI tests will be done using Python 3.7 only. Python 2.7 support
  `will be dropped in 2020`__, it's time to prepare.

  .. __: https://pythonclock.org/

- The GitLab CI tests are done using a ``debian/buster64`` Vagrant Box.

Docker
''''''

- Switch the base Docker image to `debian:buster-slim`__ and install Python 3.x
  environment instead of Python 2.7 in the DebOps Docker image.

  .. __: https://hub.docker.com/_/debian

- The :command:`docker-entrypoint` script has been refreshed to account for the
  changes in DebOps roles. The :ref:`debops.sshd` role takes care of the
  :file:`/run/sshd/` directory by itself, and running DebOps against the
  container requires :command:`sudo` access without password.

General
'''''''

- Various DebOps roles have been modified to use the :ref:`debops.keyring`
  Ansible role to manage the APT repository keys, or GPG keys on UNIX accounts.
  If you are using them in custom playbooks, you might need to update them to
  include the new dependency.

- The installation of APT and other packages in DebOps roles has been
  refactored to remove the use of the ``with_items``/``with_flattened``
  lookups. Support for package installation via task loops will be removed in
  Ansible 2.11.

- The DebOps documentation generator now supports Ansible roles with multiple
  :file:`defaults/main/*.yml` files. They are also correctly handled by the
  :command:`debops-defaults` script.

- Various DebOps roles will no longer use the hostname as a stand-in for an
  empty DNS domain when no DNS domain is detected - this resulted in the
  "standalone" hosts without a DNS domain to be misconfigured. Existing setups
  with a DNS domain shouldn't be affected, but configuration of standalone
  hosts that deploy webservices might require modifications.

- The :ref:`debops.resolvconf` role has been added as a dependency in the
  Ansible playbooks of the roles that interact with the ``resolvconf`` service
  in some way. The modified roles are: :ref:`debops.dnsmasq`,
  :ref:`debops.docker_server`, :ref:`debops.ifupdown`, :ref:`debops.lxc`,
  :ref:`debops.unbound`. The installation of the ``resolvconf`` APT package has
  been removed from the roles that contained it.

- Run :ref:`debops.apt_proxy` from the :file:`bootstrap.yml` Ansible playbook
  to ensure that if a proxy is used, it is used all the time without disabling
  the proxy for a short while during bootstrapping.
  The :file:`bootstrap-ldap.yml` Ansible playbook already included
  :ref:`debops.apt_proxy`.

User management
'''''''''''''''

- The :command:`zsh` shell APT package will be installed only if the :ref:`root
  account <debops.root_account>`, :ref:`any system users <debops.system_users>`
  or :ref:`regular users <debops.users>` managed by Ansible are using it as
  a login shell.

:ref:`debops.avahi` role
''''''''''''''''''''''''

- The :command:`avahi-alias` script has been imported into the role itself and
  will no longer be installed by cloning the upstream :command:`git`
  repository. Consequently, support for mDNS ``*.local`` CNAME resource records
  will be enabled by default on hosts with Python 2.7 installed (support for
  Python 3.x is currently not available).

:ref:`debops.dokuwiki` role
'''''''''''''''''''''''''''

- The `patchpanel DokuWiki plugin`__ has been deprecated in favor of the
  `switchpanel`__ plugin. The role will remove the ``patchpanel`` plugin
  automatically on existing installations. You might need to update the wiki
  contents to render the patch panels correctly, see the plugin documentation
  for more details.

  .. __: https://github.com/grantemsley/dokuwiki-plugin-patchpanel
  .. __: https://github.com/GreenItSolutions/dokuwiki-plugin-switchpanel

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- The ``debops.docker`` role has been renamed to :ref:`debops.docker_server` in
  preparation of adding a role that will provide client functionality like
  network and container management.

- The Docker server no longer listens on a TCP port by default, even if
  :ref:`debops.pki` is enabled.

- The default storage driver used by the :ref:`debops.docker_server` has been
  changed to ``overlay2`` which is the default in upstream. The role checks the
  currently enabled storage driver via Ansible local facts, and should preserve
  the current configuration on existing installations.

  If needed, the storage driver in use can be overridden via the
  ``docker_server__storage_driver`` variable.

:ref:`debops.etckeeper` role
''''''''''''''''''''''''''''

- The installation of :command:`etckeeper` will be disabled by default in
  Python 3.x-only environments.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The playbook will no longer force the installation of the upstream Node.js
  and Yarn packages via the :ref:`debops.nodejs` role. The upstream versions
  are currently not required on Debian Buster.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- The role will not install the ``rdnssd`` APT package if NetworkManager
  service is detected on the host, to avoid removing the NM service due to
  `package conflict`__. NetworkManager should gracefully handle adding IPv6
  nameservers to :file:`/etc/resolv.conf` file, and on systems without NM
  installed the :command:`rdnssd` script will perform this task as before.

  .. __: https://bugs.debian.org/740998

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- The role has been redesigned from scratch, and now supports multiple Debian
  Netboot installers; the iPXE scripts are defined in default variables instead
  of the file-based templates and can be easily modified via the Ansible
  inventory.

:ref:`debops.kmod` role
'''''''''''''''''''''''

- The role will use the :ref:`debops.python` Ansible role to install the
  ``kmodpy`` Python package in Python 2.7 environments. Because the package is
  not available in Debian as Python 3.x module, the ``kmod.fact`` local fact
  script will use the :command:`lsmod` command to list the kernel modules in
  this case.

- The role gained basic support for defining what kernel modules should be
  loaded on non-systemd hosts by adding them in the :file:`/etc/modules`
  configuration file.

:ref:`debops.libvirt` role
''''''''''''''''''''''''''

- The ``virt-goodies`` package will be installed only if the Python 2.7
  environment is already present on the host.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role now checks the version of the installed LXC support and uses the old
  or new configuration keys accordingly. You can review the `changed
  configuration keys`__ between the old and new LXC version for comparison.

  .. __: https://discuss.linuxcontainers.org/t/lxc-2-1-has-been-released/487

- New LXC containers will have the ``CAP_SYS_TIME`` POSIX capability dropped by
  default to ensure that time configuration is disabled inside of the
  container. This should fix an issue on Debian Buster where unprivileged LXC
  containers still have this capability enabled.

  On Debian Buster LXC hosts, the ``CAP_SYS_ADMIN`` POSIX capability will be
  dropped in new LXC containers by default.

- On Debian Buster (specifically on LXC versions below 3.1.0) the AppArmor
  restrictions on unprivileged LXC containers will be relaxed to allow correct
  operation of the :command:`systemd` service manager inside of a container.
  Check the Debian Bugs `#916644`__, `#918839`__ and `#911806`__ for reasoning
  behind this modification.

  .. __: https://bugs.debian.org/916644
  .. __: https://bugs.debian.org/918839
  .. __: https://bugs.debian.org/911806

- Restrict configuration of the :file:`poweroff.conf` :command:`systemd`
  override to Debian Stretch and Ubuntu Xenial only. The containers correctly
  shut down using ``SIGRTMIN+3`` signal on Debian Buster and beyond.

:ref:`debops.mariadb_server` role
'''''''''''''''''''''''''''''''''

- The role will no longer set a custom MariaDB ``root`` password, because the
  ``mysql_user`` Ansible 2.8 module breaks access to the MariaDB database via
  the UNIX ``root`` account by removing the ``unix_socket`` plugin access and
  not setting the ``mysql_native_password`` plugin. A password for the UNIX
  ``root`` account is not needed in the recent MariaDB releases in Debian,
  therefore this shouldn't impact the usage.

  The ``mysql_user`` Ansible module `lacks a way to control the authentication
  plugin for a given MariaDB account`__, therefore it's not advisable to mess
  with the ``root`` access to the database.

  .. __: https://github.com/ansible/ansible/issues/26581

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- Do not try to manage the hostname in LXC, Docker or OpenVZ containers by
  default. We assume that these containers are unprivileged and their hostname
  cannot be changed from the inside of the container.

- If a host does not have a proper domain, either defined locally or set via
  the DNS, don't generate a faux "domain" based on its hostname and assume that
  this is a standalone host. This might affect availability of some services,
  for example X.509 certificates managed by :ref:`debops.pki` or reachability
  of websites created on that host. In this case the host cannot have a FQDN
  defined in the Ansible inventory as the label or ``ansible_host`` variable,
  only a hostname.

- Role will check if the configured FQDN of a host exists in the DNS database.
  If it does, the entry in the :file:`/etc/hosts` file will be removed to allow
  the DNS to take over. If it doesn't, the configuration will be left intact
  with assumption that the domain is configured locally.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role will no longer default to limiting the allowed HTTP request methods
  to ``GET``, ``HEAD`` and ``POST`` on PHP-enabled websites.

:ref:`debops.pki` role
''''''''''''''''''''''

- If there is no domain set on the remote host, don't fallback to the hostname
  in the :envvar:`pki_ca_domain` variable because the generated CA certificates
  don't make any sense. With this setup the :ref:`debops.pki` role requires to
  be run against a host with a valid DNS domain for the internal CA to be
  created.

:ref:`debops.rsnapshot` role
''''''''''''''''''''''''''''

- The role has been redesigned from the ground up. Instead of using Ansible
  inventory groups to define hosts to back up, role uses a list of YAML
  dictionaries with hosts defined explicitly; the old behaviour can be
  replicated if needed. The backup host itself can also be snapshotted, with
  support for snapshots on removable media.

:ref:`debops.snmpd` role
''''''''''''''''''''''''

- The local SNMPv3 username and password will be stored in a separate file and
  retrieved via Ansible local facts, to not break Ansible fact gathering on
  unprivileged accounts. The password file is protected by strict read
  permission and accessible only by the ``root`` UNIX account.

:ref:`debops.system_groups` role
''''''''''''''''''''''''''''''''

- Don't configure the ``NOPASSWD:`` tag for the ``%admins`` and ``%wheel`` UNIX
  groups in :command:`sudo` by default when Ansible manages the local host.
  This allows local admin accounts to control ``root`` access using a password.

:ref:`debops.system_users` role
'''''''''''''''''''''''''''''''

- The role will set a custom shell based on the users' own shell for the
  dynamic UNIX account only if the shell is known by the role. This should
  avoid issues when Ansible users use non-standard shells on Ansible
  Controller.

:ref:`debops.tftpd` role
''''''''''''''''''''''''

- The role has been refreshed in conjunction with the updates to network boot
  services in preparation for Debian Buster. All of the role variables have
  been renamed to put them in their own ``tftpd__*`` namespace, and the role
  dependencies have been moved to the playbook.

:ref:`debops.unbound` role
''''''''''''''''''''''''''

- The role will enable remote control management of the :command:`unbound`
  daemon via the ``loopback`` network interface using the
  :command:`unbound-control` command.

Removed
~~~~~~~

Roles removed from DebOps
'''''''''''''''''''''''''

- The ``debops.openvz`` role has been removed. OpenVZ is not supported in
  Debian natively `since Wheezy`__; a good replacement for it is LXC which can
  be managed using the :ref:`debops.lxc` role.

  .. __: https://wiki.debian.org/OpenVz

:ref:`debops.core` role
'''''''''''''''''''''''

- The ``core__keyserver`` variable and its local fact have been removed from
  the role. They are replaced by the :envvar:`keyring__keyserver` and the
  corresponding local fact in the :ref:`debops.keyring` role.

- The :command:`resolver.fact` script has been removed from the role. Its
  functionality is provided by the :command:`resolvconf.fact` script included
  in the :ref:`debops.resolvconf` role.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Support for `ferment`__ has been removed from DebOps due to the upstream not
  being up to date anymore, both with Docker as well as with Python 3.x
  support. The :command:`dockerd` daemon will be restarted on any
  :command:`ferm` restarts to update the firewall configuration with Docker
  rules.

  .. __: https://github.com/diefans/ferment

:ref:`debops.lxc` role
''''''''''''''''''''''

- The :command:`lxc-prepare-ssh` script will no longer install SSH keys from
  the LXC host ``root`` account on the LXC container ``root`` account. This can
  cause confusion and unintended security breaches when other services (for
  example backup scripts or remote command execution tools) install their own
  SSH keys on the LXC host and they are subsequently copied inside of the LXC
  containers created on that host.

:ref:`debops.nodejs` role
'''''''''''''''''''''''''

- [debops.nodejs] Support for installing NPM from its :command:`git` repository
  has been removed. NPM is included in the NodeSource upstream ``nodejs``
  package, as well as the Debian archive since Debian Buster release in the
  ``npm`` package.

Fixed
~~~~~

:ref:`debops.apache` role
'''''''''''''''''''''''''

- Refactor the role to not use Jinja 'import' statements in looped tasks - this
  does not work on newer Jinja versions.

:ref:`debops.lvm` role
''''''''''''''''''''''

- Make sure logical volumes will only be shrunk when volume item defines
  ``force: yes``.

:ref:`debops.nsswitch` role
'''''''''''''''''''''''''''

- Don't restart the :command:`systemd-logind` service on
  :file:`/etc/nsswitch.conf` file changes if DebOps is running against
  ``localhost``, to avoid breaking the existing user session.

:ref:`debops.python` role
'''''''''''''''''''''''''

- The role should now correctly detect Python 3.x interpreter on the Ansible
  Controller and disable usage of Python 2.7 on the managed hosts.


`debops v1.0.0`_ - 2019-05-22
-----------------------------

.. _debops v1.0.0: https://github.com/debops/debops/compare/v0.8.1...v1.0.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.docker_registry` role provides support for Docker Registry.
  The role can be used as standalone or as a backend for the GitLab Container
  Registry service, with :ref:`debops.gitlab` role.

- The :ref:`debops.ldap` role sets up the system-wide LDAP configuration on
  a host, and is used as the API to the LDAP directory by other Ansible roles,
  playbooks, and users via Ansible inventory. The role is included in the
  ``common.yml`` playbook, but is disabled by default.

- The :ref:`debops.nslcd` role can be used to configure LDAP lookups for NSS
  and PAM services on a Linux host.

- The :ref:`debops.pam_access` role manages PAM access control files located in
  the :file:`/etc/security/` directory. The role is designed to allow other
  Ansible roles to easily manage their own PAM access rules.

- The :ref:`debops.yadm` role installs the `Yet Another Dotfiles Manager`__
  script and ensures that additional shells are available. It can also mirror
  dotfiles locally. The role is included in the common playbook.

  .. __: https://yadm.io/

- The :ref:`debops.system_users` role replaces the ``debops.bootstrap`` role
  and is used to manage the local system administrator accounts. It is included
  in the :file:`common.yml` playbook as well as the bootstrap playbooks.

General
'''''''

- The DebOps project has been registered `in the IANA Private Enterprise
  Numbers`__ registry, with PEN number ``53622``. The project documentation
  contains :ref:`an OID registry <debops_oid_registry>` to track custom LDAP
  schemas, among other things.

  .. __: https://www.iana.org/assignments/enterprise-numbers/enterprise-numbers

- Support for Ansible Collections managed by the `Mazer`__ Content Manager has
  been implemented in the repository. Ansible Collections will be usable after
  June 2019, when support for them is enabled in the Ansible Galaxy service.

  .. __: https://github.com/ansible/mazer

LDAP
''''

- A new :file:`bootstrap-ldap.yml` Ansible playbook can be used to bootstrap
  Debian/Ubuntu hosts with LDAP support enabled by default. The playbook will
  configure only the services required for secure LDAP access (PKI, SSH,
  PAM/NSS), the rest should be configured using the common playbook.

:ref:`debops.ansible_plugins` role
''''''''''''''''''''''''''''''''''

- A new ``ldap_attrs`` Ansible module has been added to the role. It's
  a replacement for the ``ldap_attr`` core Ansible module, that's more in line
  with the ``ldap_entry`` module. Used by the :ref:`debops.slapd` and
  :ref:`debops.ldap` roles to manage the LDAP directory contents.

:ref:`debops.apt` role
''''''''''''''''''''''

- Systems with the End of Life Debian releases (``wheezy``) installed will be
  configured to use the Debian Archive repository as the main APT sources
  instead of the normal Debian repository mirrors. These releases have been
  moved out of the main repositories and are not fully available through normal
  means. The periodic updates of the APT archive repositories on these systems
  will be disabled via the :ref:`debops.unattended_upgrades` role, since the
  EOL releases no longer receive updates.

  The Debian LTS release (``jessie``) APT repository sources will use only the
  main and security repositories, without updates or backports. See the
  `information about the Debian LTS support`__ for more details.

  .. __: https://wiki.debian.org/LTS

:ref:`debops.lxc` role
''''''''''''''''''''''

- Users can now disable default route advertisement in the ``lxc-net`` DHCP
  service. This is useful in cases where LXC containers have multiple network
  interfaces and the default route should go through a different gateway than
  the LXC host.

- The :command:`lxc-new-unprivileged` script will add missing network interface
  stanzas in the container's :file:`/etc/network/interfaces` file, by default
  with DHCP configuration. This will happen only on the initialization of the
  new container, when a given LXC container has multiple network interfaces
  defined in its configuration file.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role will automatically generate configuration which redirects short
  hostnames or subdomains to their FQDN equivalents. This allows HTTP clients
  to reach websites by specifying their short names via DNS suffixes from
  :file:`/etc/resolv.conf` file, or using ``*.local`` domain names managed by
  Avahi/mDNS to redirect HTTP clients to the correct FQDNs.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- Some lists can now configure ACL entries on the destination files or
  directories using the ``item.acl`` parameter. Take a look to
  :ref:`resources__ref_acl` section to have the list of compatibles variables.

- New :ref:`resources__ref_commands` variables can be used to define simple
  shell commands or scripts that will be executed at the end of the
  :ref:`debops.resources` role. Useful to start new services, but it shouldn't
  be used as a replacement for a fully-fledged Ansible roles.

:ref:`debops.sudo` role
'''''''''''''''''''''''

- The role is now integrated with the :ref:`debops.ldap` Ansible role and can
  configure the :command:`sudo` service to read ``sudoers`` configuration from
  the LDAP directory.

:ref:`debops.users` role
''''''''''''''''''''''''

- The role can now configure UNIX accounts with access restricted to SFTP
  operations (SFTPonly) with the new ``item.chroot`` parameter. This is
  a replacement for the ``debops.sftpusers`` role.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- The :ref:`debops.gitlab` role will install GitLab 11.10 on supported
  platforms (Debian Buster, Ubuntu Bionic), existing installations will be
  upgraded.

- In the :ref:`debops.phpipam` role, the relevant inventory variables have
  been renamed, check the :ref:`upgrade_notes` for details. The role now uses
  the upstream phpIPAM repository and it installs version 1.3.2.

- In the :ref:`debops.php` role, because of the PHP 7.0 release status
  changed to `End of life`__ at the beginning of 2019, Ondřej Surý APT
  repository with PHP 7.2 packages will be enabled by default on Debian
  Jessie and Stretch as well as Ubuntu Trusty and Xenial. Existing
  :ref:`debops.php` installations shouldn't be affected, but the role will
  not try to upgrade the PHP version either.  Users should consider upgrading
  the packages manually or reinstalling services from scratch with the newer
  version used by default.

  .. __: https://secure.php.net/supported-versions.php

- In the :ref:`debops.rstudio_server` role, the supported version has been
  updated to v1.2.1335. The role no longer installs ``libssl1.0.0`` from
  Debian Jessie on Debian Stretch, since the current version of the RStudio
  Server works in the default Stretch environment. The downloaded ``.deb``
  package will be verified using the RStudio Inc. GPG signing key before
  installation.

- In the :ref:`debops.docker_gen` role, the docker-gen version that this role
  installs by default has been updated to version 0.7.4. This release notably
  adds IPv6 and docker network support.

General
'''''''

- The :ref:`debops.cron` role will be applied much earlier in the
  ``common.yml`` playbook because the :ref:`debops.pki` role depends on
  presence of the :command:`cron` daemon on the host.

- Bash scripts and ``shell``/``command`` Ansible modules now use relative
  :command:`bash` interpreter instead of an absolute :file:`/bin/bash`. This
  should help make the DebOps roles more portable, and prepare the project for
  the merged :file:`/bin` and :file:`/usr/bin` directories in a future Debian
  release.

Mail Transport Agents
'''''''''''''''''''''

- The :file:`/etc/mailname` configuration file will contain the DNS domain of
  a host instead of the FQDN address. This will result in the mail senders that
  don't specify the domain part to have the DNS domain, instead of the full
  host address, added by the Mail Transport Agent. This configuration should
  work better in clustered environments, where there is a central mail hub/MX
  that receives the mail and redirects it.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The GitLab playbook will import the :ref:`debops.docker_registry` playbook to
  ensure that configuration related to Docker Registry defined in the GitLab
  service is properly applied during installation/management.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The :command:`lxc-prepare-ssh` script will read the public SSH keys from
  specific files (``root`` key file, and the ``$SUDO_USER`` key file) and will
  not accept any custom files to read from, to avoid possible security issues.
  Each public SSH key listed in the key files is validated before being added
  to the container's ``root`` account.

  The :command:`lxc-new-unprivileged` script will similarly not accept any
  custom files as initial LXC container configuration to fix any potential
  security holes when used via :command:`sudo`. The default LXC configuration
  file used by the script can be configured in :file:`/etc/lxc/lxc.conf`
  configuration file.

:ref:`debops.mariadb_server` role
'''''''''''''''''''''''''''''''''

- The MariaDB user ``root`` is no longer dropped. This user is used for
  database maintenance and authenticates using the ``unix_auth`` plugin.
  However, DebOps still maintains and sets a password for the ``root`` UNIX
  account, stored in the :file:`/root/.my.cnf` config file.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- The role will be disabled by default in Docker containers.  In this
  environment, the :file:`/etc/hosts` file is managed by Docker and cannot be
  modified from inside of the container.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- The role will not perform any tasks related to :command:`occ` command if the
  automatic setup is disabled in the :envvar:`owncloud__autosetup` variable. In
  this mode, the :command:`occ` tasks cannot be performed by the role because
  the ownCloud/Nextcloud installation is not finished. The users are expected
  to perform necessary tasks themselves if they decide to opt-out from the
  automatic configuration.

:ref:`debops.php` role
''''''''''''''''''''''

- The PHP version detection has been redesigned to use the :command:`apt-cache
  madison` command to find the available versions. The role will now check the
  current version of the ``php`` APT package to select the available stable PHP
  version. This unfortunately breaks support for the ``php5`` packages, but the
  ``php5.6`` packages from Ondřej Surý APT repository work fine.

- The role will install the :command:`composer` command from the upstream
  GitHub repository on older OS releases, including Debian Stretch (current
  Stable release). This is due to incompatibility of the ``composer`` APT
  package included in Debian Stretch and PHP 7.3.

  The custom ``composer`` command installation tasks have been removed from the
  :ref:`debops.roundcube` and :ref:`debops.librenms` roles, since
  :ref:`debops.php` will take care of the installation.

:ref:`debops.root_account` role
'''''''''''''''''''''''''''''''

- If the :ref:`debops.ldap` Ansible role has been applied on a host, the
  :ref:`debops.root_account` role will use the UID/GID ranges defined by it,
  which include UIDs/GIDs used in the LDAP directory, to define subUID/subGID
  range of the ``root`` account. This allows usage of the LDAP directory as
  a source of UNIX accounts and groups in unprivileged containers.  Existing
  systems will not be changed.

- Management of the ``root`` dotfiles has been removed from the
  :ref:`debops.users` role and is now done in the :ref:`debops.root_account`
  role, using the :command:`yadm` script. Users might need to clean out the
  existing dotfiles if they were managed as symlinks, otherwise :command:`yadm`
  script will not be able to correctly deploy the new dotfiles.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The role has been redesigned from the ground up, with support for N-Way
  Multi-Master replication, custom LDAP schemas, Password Policy and other
  functionality. The role uses custom ``ldap_attrs`` Ansible module included in
  the :ref:`debops.ansible_plugins` role for OpenLDAP management.

  The OpenLDAP configuration will definitely break on existing installations.
  It's best to set up a new OpenLDAP server (or replicated cluster) and import
  the LDAP directory to it afterwards. See :ref:`role documentation
  <debops.slapd>` for more details.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The access control based on UNIX groups defined in the
  :file:`/etc/ssh/sshd_config` file has been removed. Instead, the OpenSSH
  server uses the PAM access control configuration, managed by the
  :ref:`debops.pam_access` Ansible role, to control access by
  users/groups/origins. OpenSSH service uses its own access control file,
  separate from the global :file:`/etc/security/access.conf` file.

- The role will enable client address resolving using DNS by setting the
  ``UseDNS yes`` option in OpenSSH server configuration. This parameter is
  disabled by default in Debian and upstream, however it is required for the
  domain-based access control rules to work as expected.

- When the LDAP support is configured on a host by the :ref:`debops.ldap` role,
  the :ref:`debops.sshd` role will use the resulting infrastructure to connect
  to the LDAP directory and create the ``sshd`` LDAP account object for each
  host, used for lookups of the SSH keys in the directory. The SSH host public
  keys will be automatically added or updated in the LDAP device object to
  allow for centralized generation of the ``~/.ssh/known_hosts`` files based on
  the data stored in LDAP.

  The role will no longer create a separate ``sshd-lookup`` UNIX account to
  perform LDAP lookups; the existing ``sshd`` UNIX account will be used
  instead. The :command:`ldapsearch` command used for lookups will default to
  LDAP over TLS connections instead of LDAPS.

:ref:`debops.system_groups` role
''''''''''''''''''''''''''''''''

- If the LDAP support is enabled on a host via the :ref:`debops.ldap` role, the
  UNIX system groups created by the :ref:`debops.system_groups` role by default
  will use a ``_`` prefix to make them separate from any LDAP-based groups of
  the same name. Existing installations should be unaffected, as long as the
  updated :ref:`debops.system_groups` role was applied before the
  :ref:`debops.ldap` role.

:ref:`debops.unattended_upgrades` role
''''''''''''''''''''''''''''''''''''''

- The packages from the ``stable-updates`` APT repository section will be
  automatically upgraded by default, the same as the packages from Debian
  Security repository. This should cover important non-security related
  upgrades, such as timezone changes, antivirus database changes, and similar.

- If automatic reboots are enabled, VMs will not reboot all at the same time to
  avoid high load on the hypervisor host.  Instead they will reboot at
  a particular minute in a 15 minute time window.  For each host, a
  random-but-idempotent time is chosen.  For hypervisor hosts good presets
  cannot be picked. You should ensure that hosts don’t reboot at the same time
  by defining different reboot times in inventory groups.

:ref:`debops.users` role
''''''''''''''''''''''''

- The management of the user dotfiles in the :ref:`debops.users` role has been
  redesigned and now uses the :command:`yadm` script to perform the actual
  deployment. See :ref:`debops.yadm` for details about installing the script
  and creating local dotfile mirrors. The :ref:`users__ref_accounts` variable
  documentation contains examples of new dotfile definitions.

- The role now uses the ``libuser`` library via the Ansible ``group`` and
  ``user`` modules to manage local groups and accounts. This should avoid
  issues with groups and accounts created in the LDAP user/group ranges.

  The ``libuser`` library by default creates home directories with ``0700``
  permissions, which is probably too restrictive. Because of that, the role
  will automatically change the home directory permissions to ``0751`` (defined
  in the :envvar:`users__default_home_mode` variable). This also affects
  existing UNIX accounts managed by the role; the mode can be overridden using
  the ``item.home_mode`` parameter.

- The ``users__*_resources`` variables have been reimplemented as the
  ``item.resources`` parameter of the ``users__*_accounts`` variables.  This
  removes the unnecessary split between user account definitions and
  definitions of their files/directories.

Removed
~~~~~~~

Roles removed from DebOps
'''''''''''''''''''''''''

- The ``debops.sftpusers`` Ansible role has been removed. Its functionality is
  now implemented by the :ref:`debops.users` role, custom bind mounts can be
  defined using the :ref:`debops.mount` role.

- The ``debops.bootstrap`` Ansible role has been removed. Its replacement is
  the :ref:`debops.system_users` which is used to manage system administrator
  accounts, via the ``common.yml`` playbook and the bootstrap playbooks.

:ref:`debops.auth` role
'''''''''''''''''''''''

- The :file:`/etc/ldap/ldap.conf` file configuration, :command:`nslcd` service
  configuration and related variables have been removed from the
  :ref:`debops.auth` role. This functionality is now available in the
  :ref:`debops.ldap` and :ref:`debops.nslcd` roles, which manage the
  client-side LDAP support.

:ref:`debops.rstudio_server` role
'''''''''''''''''''''''''''''''''

- The role will no longer install the historical ``libssl1.0.0`` APT package on
  Debian Stretch to support older RStudio Server releases. You should remove it
  on the existing installations after RStudio Server is upgraded to the newest
  release.

Fixed
~~~~~

:ref:`debops.authorized_keys` role
''''''''''''''''''''''''''''''''''

- Set the group for authorized_keys files to the primary group of the user
  instead of the group with the same name as the user. This is important
  because otherwise the readonly mode of the role does not work when the
  primary group of a user has a different name then the username.

:ref:`debops.lvm` role
''''''''''''''''''''''

- Make sure a file system is created by default when the ``mount`` parameter is
  defined in the :envvar:`lvm__logical_volumes`.

- Stop and disable ``lvm2-lvmetad.socket`` systemd unit when disabling
  :envvar:`lvm__global_use_lvmetad` to avoid warning message when invoking LVM
  commands.

:ref:`debops.redis_server` role
'''''''''''''''''''''''''''''''

- Use the :file:`redis.conf` file to lookup passwords via the
  :command:`redis-password` script. This file has the ``redis-auth`` UNIX group
  and any accounts in this group should now be able to look up the Redis
  passwords correctly.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The role will check if the X.509 certificate and the private key used for TLS
  communication were correctly configured in the OpenLDAP server. This fixes an
  issue where configuration of the private key and certificate was not
  performed at all, without any actual changes in the service, with subsequent
  task exiting with an error due to misconfiguration.

Security
~~~~~~~~

:ref:`debops.php` role
''''''''''''''''''''''

- Ondřej Surý `created new APT signing keys`__ for his Debian APT repository
  with PHP packages, due to security concerns. The :ref:`debops.php` role will
  remove the old APT GPG key and add the new one automatically.

  .. __: https://www.patreon.com/posts/dpa-new-signing-25451165


`debops v0.8.1`_ - 2019-02-02
-----------------------------

.. _debops v0.8.1: https://github.com/debops/debops/compare/v0.8.0...v0.8.1

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.redis_server` and :ref:`debops.redis_sentinel` roles, that
  replace the existing ``debops.redis`` Ansible role. The new roles support
  multiple Redis and Sentinel instances on a single host.

- The :ref:`debops.freeradius` role can be used to manage FreeRADIUS service,
  used in network management.

- The :ref:`debops.dhcp_probe` role can be used to install and configure
  :command:`dhcp_probe` service, which passively detects rogue DHCP servers.

- The :ref:`debops.mount` role allows configuration of :file:`/etc/fstab`
  entries for local devices, bind mounts and can be used to create or modify
  directories, to permit access to resources by different applications. The
  role is included by default in the ``common.yml`` playbook.

Continuous Integration
''''''''''''''''''''''

- Ansible roles included in DebOps are now checked using `ansible-lint`__ tool.
  All existing issues found by the script have been fixed.

  .. __: https://docs.ansible.com/ansible-lint/

- The hosts managed by the DebOps Vagrant environment will now use Avahi to
  detect multiple cluster nodes and generate host records in the
  :file:`/etc/hosts` database on these nodes. This allows usage of real DNS
  FQDNs and hostnames in the test environment without reliance on an external
  DHCP/DNS services.

General
'''''''

- DebOps roles are now tagged with ``skip::<role_name>`` Ansible tags. You can
  use these tags to skip roles without any side-effects; for example
  "<role_name>/env" sub-roles will still run so that roles that depend on them
  will work as expected.

- You can use the :command:`make versions` command in the root of the DebOps
  monorepo to check currently "pinned" and upstream versions of third-party
  software installed and managed by DebOps, usually via :command:`git`
  repositories. This requires the :command:`uscan` command from the Debian
  ``devscripts`` APT package to be present.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- The role will now generate configuration for the :ref:`debops.sysctl` role
  and use it in the playbook as a dependency, to configure kernel parameters
  related to packet forwarding on managed network interfaces. This
  functionality replaces centralized configuration of packet forwarding on all
  network interfaces done by the :ref:`debops.ferm` role.

:ref:`debops.lxc` role
''''''''''''''''''''''

- New :command:`lxc-hwaddr-static` script can be used to easily generate random
  but predictable MAC addresses for LXC containers.

  The script can be run manually or executed as a "pre-start" LXC hook to
  configure static MAC addresses automatically - this usage is enabled by
  default via common LXC container configuration.

- The `lxc_ssh.py <https://github.com/andreasscherbaum/ansible-lxc-ssh>`__
  Ansible connection plugin is now included by default in DebOps. This
  connection plugin can be used to manage remote LXC containers with Ansible
  via SSH and the :command:`lxc-attach` command. This requires connection to
  the LXC host and the LXC container via the ``root`` account directly, which
  is supported by the DebOps playbooks and roles.

- The role can now manage LXC containers, again. This time the functionality is
  implemented using the ``lxc_container`` Ansible module instead of a series of
  shell tasks. By default unprivileged LXC containers will be created, but
  users can change all parameters supported by the module.

- The role will now configure a ``lxcbr0`` bridge with internal DNS/DHCP server
  for LXC containers, using the ``lxc-net`` service. With this change, use of
  the :ref:`debops.ifupdown` role to prepare a default bridge for LXC
  containers is not required anymore.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- When a large number of hosts is defined for the :file:`/etc/hosts` database,
  the role will switch to generating the file using the ``template`` Ansible
  module instead of managing individual lines using the ``lineinfile`` module,
  to make the operation faster. As a result, custom modifications done by other
  tools in the host database will not be preserved.

- The role can now configure the hostname in the :file:`/etc/hostname` file, as
  well as the local domain configuration in :file:`/etc/hosts` database.

:ref:`debops.php` role
''''''''''''''''''''''

- The role will install the ``composer`` APT package on Debian Stretch, Ubuntu
  Xenial and their respective newer OS releases.

:ref:`debops.root_account` role
'''''''''''''''''''''''''''''''

- The role will reserve a set of UID/GID ranges for subordinate UIDs/GIDs owned
  by the ``root`` account (they are not reserved by default). This can be used
  to create unprivileged LXC containers owned by ``root``. See the release
  notes for potential issues on existing systems.

- You can now configure the state and contents of the
  :file:`/root/.ssh/authorized_keys` file using the :ref:`debops.root_account`
  role, with support for global, per inventory group and per host SSH keys.

:ref:`debops.users` role
''''''''''''''''''''''''

- The role can now configure ACL entries of the user home directories using the
  ``item.home_acl`` parameter. This can be used for more elaborate access
  restrictions.

Changed
~~~~~~~

Continuous Integration
''''''''''''''''''''''

- The test suite will now check POSIX shell scripts along with Bash scripts for
  any issues via the :command:`shellcheck` linter. Outstanding issues found in
  existing scripts have been fixed.

General
'''''''

- The :ref:`debops.root_account` role will be executed earlier in the
  ``common.yml`` Ansible playbook to ensure that the ``root`` UID/GID ranges
  are reserved without issues on the initial host configuration.

- Various filter and lookup Ansible plugins have been migrated from the
  playbook directory to the :ref:`debops.ansible_plugins` role. This role can
  be used as hard dependency in other Ansible roles that rely on these plugins.

- The order of the roles in the common playbook has been changed; the
  :ref:`debops.users` role will be applied before the :ref:`debops.resources`
  role to allow for resources owned by UNIX accounts/groups other than
  ``root``.

- The ``debops`` Python package has dropped the hard dependency on Ansible.
  This allows DebOps to be installed in a separate environment than Ansible,
  allowing for example to mix Homebrew Ansible with DebOps from PyPI on macOS.
  The installation instructions have also been updated to reflect the change.

- The :command:`debops-init` script will now generate new Ansible inventory
  files using the hostname as well as a host FQDN to better promote the use of
  DNS records in Ansible inventory.

:ref:`debops.dnsmasq` role
''''''''''''''''''''''''''

- The role has been redesigned from the ground up with new configuration
  pipeline, support for multiple subdomains and better default configuration.
  See the :ref:`debops.dnsmasq` role documentation as well as the
  :ref:`upgrade_notes` for more details.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- If the Docker host uses a local nameserver, for example :command:`dnsmasq` or
  :command:`unbound`, Docker containers might have misconfigured DNS nameserver
  in :file:`/etc/resolv.conf` pointing to ``127.0.0.1``. In these cases, the
  :ref:`debops.docker_server` role will configure Docker to use the upstream
  nameservers from the host, managed by the ``resolvconf`` APT package.

  If no upstream nameservers are available, the role will not configure any
  nameserver and search parameters, which will tell Docker to use the Google
  nameservers.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The role will now install GitLab 10.8 by default, on Debian Stretch and
  Ubuntu Xenial. The 11.x release now requires Ruby 2.4+, therefore it will
  only be installed on newer OS releases (Debian Buster, Ubuntu Bionic).

- The role has been updated to use Ansible local facts managed by the
  :ref:`debops.redis_server` Ansible role. Redis Server support has been
  removed from the GitLab playbook and needs to be explicitly enabled in the
  inventory for GitLab to be installed correctly. This will allow to select
  between local Server or Sentinel instance, to support clustered environments.

  Check the :ref:`upgrade_notes` for issues with upgrading Redis Server support
  on existing GitLab hosts.

:ref:`debops.grub` role
'''''''''''''''''''''''

- The GRUB configuration has been redesigned, role now uses merged variables to
  make configuration via Ansible inventory or dependent role variables easier.
  The GRUB configuration is now stored in the :file:`/etc/default/grub.d/`
  directory to allow for easier integration with other software. See the
  :ref:`debops.grub` documentation for more details.

- The user password storage path in :file:`secret/` directory has been changed
  to use the ``inventory_hostname`` variable instead of the ``ansible_fqdn``
  variable. This change will force regeneration of password hashes in existing
  installations, but shouldn't affect host access (passwords stay the same).

:ref:`debops.gunicorn` role
'''''''''''''''''''''''''''

- The role depends on :ref:`debops.python` now to install the required
  packages. Please update your custom playbooks accordingly.

:ref:`debops.ipxe` role
'''''''''''''''''''''''

- The role will no longer install non-free firmware by default.  This is done
  to solve the connectivity issues with ``cdimage.debian.org`` host.

:ref:`debops.librenms` role
'''''''''''''''''''''''''''

- The default dashboard in LibreNMS is changed from the
  :file:`pages/front/default.php` to :file:`pages/front/tiles.php` which allows
  for better customization.

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role will configure the default subUIDs and subGIDs for unprivileged LXC
  containers based on the configured subordinate UID/GID ranges for the
  ``root`` account.

- The :command:`lxc-prepare-ssh` script will now install SSH public keys from
  the user account that is running the script via :command:`sudo` instead of
  the system's ``root`` account, which is usually what you want to do if other
  people manage their own LXC containers on a host.

- The LXC configuration managed by the role will use the :command:`systemd`
  ``lxc@.service`` instances to manage the containers instead of using the
  :command:`lxc-*` commands directly. This allows the containers to be shut
  down properly without hitting a timeout and forced killing of container
  processes.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- The role will now use Ansible facts managed by the :ref:`debops.redis_server`
  role to configure Redis support.

- Drop support for Nextcloud 12.0 which is EOF. Add support for Nextcloud 14.0
  and 15.0 and make Nextcloud 14.0 the default Nextcloud version.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- The hostname and domain configuration during bootstrapping is now done by the
  :ref:`debops.netbase` Ansible role. The default for this role is to remove
  the ``127.0.1.1`` host entry from the :file:`/etc/hosts` file to ensure that
  domain resolution relies on DNS.

  If you are using local domain configured in :file:`/etc/hosts` file, you
  should define the :envvar:`netbase__domain` variable in the Ansible inventory
  with your desired domain.

- The role is redesigned to use list variables instead of YAML dictionaries for
  the :file:`/etc/hosts` database. This allows for adding the host IPv4 and/or
  IPv6 addresses defined by Ansible facts when the custom local domain is
  enabled. See :ref:`netbase__ref_hosts` for details.  The role has also been
  included in the ``common.yml`` playbook to ensure that the host database is
  up to date as soon as possible.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- Changed behaviour of used groups for templating. Now all groups the host is
  in, will be used to search for template files.  Read the documentation about
  :ref:`resources__ref_templates` for more details on templating with `debops`.

Fixed
~~~~~

:ref:`debops.grub` role
'''''''''''''''''''''''

- The role should now correctly revert custom patch to allow user
  authentication in :file:`/etc/grub.d/10_linux` script, when the user list is
  empty.

:ref:`debops.kmod` role
'''''''''''''''''''''''

- The role should now work correctly in Ansible ``--check`` mode before the
  Ansible local fact script is installed.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The role should correctly handle nested lists in role dependent variables,
  which are now flattened before being passed to the configuration filter.

Removed
~~~~~~~

Roles removed from DebOps
'''''''''''''''''''''''''

- The old ``debops.redis`` Ansible role has been removed. It has been replaced
  by the :ref:`debops.redis_server` and :ref:`debops.redis_sentinel` Ansible
  roles. The new roles use their own Ansible inventory groups, therefore they
  will need to be explicitly enabled to affect existing hosts.

  You can use the :ref:`debops.debops_legacy` Ansible role to clean up old
  configuration files, directories and diversions of ``debops.redis`` role from
  remote hosts.

General
'''''''

- The ``ldap_entry`` and ``ldap_attr`` Ansible modules have been removed. They
  are now included in Ansible core, there's no need to keep a separate copy in
  the playbook.

:ref:`debops.core` role
'''''''''''''''''''''''

- The ``ansible_local.root.flags`` and ``ansible_local.root.uuid`` local facts
  have been removed. They are replaced by ``ansible_local.tags`` and
  ``ansible_local.uuid`` local facts, respectively.

:ref:`debops.dhcpd` role
''''''''''''''''''''''''

- Support for :command:`dhcp_probe` has been removed from the
  :ref:`debops.dhcpd` Ansible role. It's now available as a separate
  :ref:`debops.dhcp_probe` role.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- Automated configuration of packet forwarding with ``FORWARD`` chain rules and
  :command:`sysctl` configuration has been removed from the role. Per-interface
  packet forwarding is now configurable using the :ref:`debops.ifupdown` role,
  and you can still use the :ref:`debops.ferm` and :ref:`debops.sysctl` roles
  to design custom forwarding configuration.

  Support for this mechanism has also been removed from related roles like
  :ref:`debops.libvirtd` and :ref:`debops.lxc`.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- The hostname and domain configuration has been removed from the
  ``debops.bootstrap`` role. This functionality is now handled by the
  :ref:`debops.netbase` role, which has been included in the bootstrap
  playbook. The relevant inventory variables have been renamed, check the
  :ref:`upgrade_notes` for details.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- The ``resources__group_name`` variable has been removed in favor of using
  all the groups the current hosts is in. This change has been reflected in the
  updated variable ``resources__group_templates``.


`debops v0.8.0`_ - 2018-08-06
-----------------------------

.. _debops v0.8.0: https://github.com/debops/debops/compare/v0.7.2...v0.8.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.netbase` role: manage local host and network database in
  :file:`/etc/hosts` and :file:`/etc/networks` files.

- The :ref:`debops.sudo` role: install and manage :command:`sudo`
  configuration on a host. The role is included in the ``common.yml``
  playbook.

- The :ref:`debops.system_groups` role: configure UNIX system groups used on
  DebOps hosts. The role is included in the ``common.yml`` playbook.

- The :ref:`debops.debops_legacy` role: clean up legacy files, directories,
  APT packages or :command:`dpkg-divert` diversions created by DebOps but no
  longer used. This role needs to be executed manually, it's not included in
  the main playbook.

- The :ref:`debops.python` role: manage Python environment, with support for
  multiple Python versions used at the same time. The role is included in the
  ``common.yml`` playbook.

- Icinga 2 support has been implemented with :ref:`debops.icinga`,
  :ref:`debops.icinga_db` and :ref:`debops.icinga_web` Ansible roles.

General
'''''''

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

:ref:`debops.dhparam` role
''''''''''''''''''''''''''

- The role will set up a :command:`systemd` timer to regenerate Diffie-Hellman
  parameters periodically if it's available. The timer will use random delay
  time, up to 12h, to help with mass DHparam generation in multiple LXC
  containers/VMs.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- A ``default`` set of SSL ciphers can be specified using the
  :envvar:`nginx_default_ssl_ciphers` variable. This disables the
  ``ssl_ciphers`` option in the :command:`nginx` configuration and forces the
  server to use the defaults provided by the OS.

:ref:`debops.ntp` role
''''''''''''''''''''''

- The OpenNTPD service will now properly integrate the :command:`ifupdown` hook
  script with :command:`systemd`. During boot, NTP daemon will be started once
  network interfaces are configured and will not restart multiple times on each
  network interface change.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- The role can now generate custom files using templates, based on a directory
  structure. See :ref:`resources__ref_templates` for more details.

:ref:`debops.sudo` role
'''''''''''''''''''''''

- You can now manage configuration files located in the :file:`/etc/sudoers.d/`
  directory using :ref:`sudo__*_sudoers <sudo__ref_sudoers>` inventory
  variables, with multiple level of conditional options.

:ref:`debops.users` role
''''''''''''''''''''''''

- Selected UNIX accounts can now be configured to linger when not logged in via
  the ``item.linger`` parameter. This allows these accounts to maintain
  long-running services when not logged in via their own private
  :command:`systemd` instances.

Changed
~~~~~~~

General
'''''''

- Some of the existing DebOps Policies and Guidelines have been reorganized and
  the concept of DebOps Enhancement Proposals (DEPs) is introduced, inspired by
  the `Python Enhancement Proposals`__.

.. __: https://www.python.org/dev/peps/pep-0001/

- The :command:`debops` script can now parse multiple playbook names specified
  in any order instead of just looking at the first argument passed to it.

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- The :command:`editor` alternative symlink configuration has been moved from
  the ``debops.console`` role to the :ref:`debops.apt_install` role which also
  installs :command:`vim` by default.

:ref:`debops.apt_mark` role
'''''''''''''''''''''''''''

- The configuration of automatic removal of APT packages installed via
  ``Recommends:`` or ``Suggests:`` dependencies has been moved from the
  :ref:`debops.apt` role to the :ref:`debops.apt_mark` role which more closely
  reflects its intended purpose. Variable names and their default values
  changed; see the :ref:`upgrade_notes` for more details.

:ref:`debops.core` role
'''''''''''''''''''''''

- The role will add any new administrator accounts to the list of existing
  admin accounts instead of replacing them in the Ansible local fact script.
  This should allow for multiple administrators to easily coexist and run the
  DebOps playbooks/roles from their own accounts without issues.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- Redesign the GitLab version management to read the versions of various
  components from the GitLab repository files instead of managing them manually
  in a YAML dictionary. The new ``gitlab__release`` variable is used to
  specify desired GitLab version to install/manage.

- The :command:`gitaly` service will be installed using the ``git`` UNIX
  account instead of ``root``. Existing installations might require additional
  manual cleanup; see the :ref:`upgrade_notes` for details.

- The role now supports installation of GitLab 10.7.

- The usage of :envvar:`gitlab__fqdn` variable is revamped a bit - it's now
  used as the main variable that defines the GitLab installation FQDN. You
  might need to update the Ansible inventory if you changed the value of the
  ``gitlab_domain`` variable used previously for this purpose.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- The :ref:`debops.kmod` role is added as a dependency. The
  :ref:`debops.ifupdown` role will generate :command:`modprobe` configuration
  based on the type of configured network interfaces (bridges, VLANs, bonding)
  and the kernel modules will be automatically loaded if missing.

:ref:`debops.lxc` role
''''''''''''''''''''''

- Redesign system-wide LXC configuration to use list of YAML dictionaries
  merged together instead of custom Jinja templates.

- Add :command:`lxc-prepare-ssh` script on the LXC hosts that can be used to
  install OpenSSH and add the user's SSH authorized keys inside of the LXC
  containers. This is a new way to prepare the LXC containers for
  Ansible/DebOps management that doesn't require custom LXC template scripts
  and can be used with different LXC container types.

:ref:`debops.mariadb_server` role
'''''''''''''''''''''''''''''''''

- The MariaDB/MySQL server and :ref:`client <debops.mariadb>` will now use the
  ``utf8mb4`` encoding by default instead of the ``utf8`` which is an internal
  MySQL character encoding. This might impact existing databases, see the
  :ref:`upgrade_notes` for details.

:ref:`debops.nodejs` role
'''''''''''''''''''''''''

- The NPM version installed by the role from GitHub is changed from ``v5.4.2``
  to ``latest`` which seems to be an equivalent of a stable branch.

- Recent versions of NPM `require NodeJS 6.0.0+`__ and don't work with other
  releases. Because of that the newest NPM release is not installable on hosts
  that use NodeJS packages from older OS releases.

  .. __: https://github.com/npm/npm/issues/20425

  The :ref:`debops.nodejs` role will install NPM v5.10.0 version in this case
  to allow NPM to work correctly - on Debian Jessie, Stretch and Ubuntu Xenial.
  Otherwise, a NPM from the ``latest`` branch will be installed, as before.

- Instead of NodeJS 6.x release, the role will now install NodeJS 8.x release
  upstream APT packages by default. This is due to the NodeJS 6.x release
  `switching to a Maintenance LTS mode`__. NodeJS 8.x will be supported as
  a LTS release until April 2019.

  .. __: https://github.com/nodejs/Release

- The role will install upstream NodeSource APT packages by default. This is
  due to `no security support in Debian Stable`__, therefore an upstream
  packages should be considered more secure. The upstream NodeJS packages
  include a compatible NPM release, therefore it won't be separately installed
  from GitHub.

  .. __: https://www.debian.org/releases/stretch/amd64/release-notes/ch-information.en.html#libv8

  The existing installations shouldn't be affected, since the role will select
  OS/upstream package versions based on existing Ansible local facts.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- Support Nextcloud 13 and partially ownCloud 10. Nextcloud 11 and ownCloud 9.1
  are EOL, you should update. The role can help you with the update to ensure
  that everything works smoothly with the new versions.  Currently, the role
  can not do the update for you.

:ref:`debops.sshd` role
'''''''''''''''''''''''

- The role will now check the :ref:`debops.system_groups` Ansible local facts
  to define what UNIX groups are allowed to connect to the host via the SSH
  service.

:ref:`debops.unattended_upgrades` role
''''''''''''''''''''''''''''''''''''''

- On hosts without a domain set, the role enabled all upgrades, not just
  security updates. This will not happen anymore, the security updates are
  enabled everywhere by default, you need to enable all upgrades specifically
  via the :envvar:`unattended_upgrades__release` variable.

Removed
~~~~~~~

:ref:`debops.apt_install` role
''''''''''''''''''''''''''''''

- Don't install the ``sudo`` package by default, this is now done via
  a separate :ref:`debops.sudo` role to easily support switching to the
  ``sudo-ldap`` APT package.

:ref:`debops.auth` role
'''''''''''''''''''''''

- Remove configuration of UNIX system groups and accounts in the ``admins``
  UNIX group. This is now done by the :ref:`debops.system_groups` Ansible role.

``debops.console`` role
'''''''''''''''''''''''

- Remove support for copying custom files from the role. This functionality is
  covered better by the :ref:`debops.resources` role.

- Remove support for managing entries in the :file:`/etc/hosts` database. This
  is now covered by the :ref:`debops.netbase` Ansible role.

``debops.bootstrap`` role
'''''''''''''''''''''''''

- The :command:`sudo` configuration has been removed from the
  ``debops.bootstrap`` role. The ``bootstrap.yml`` playbook now includes the
  :ref:`debops.sudo` role which configures :command:`sudo` service.

- The UNIX system group management has been removed from the role, the
  ``bootstrap.yml`` playbook now uses the :ref:`debops.system_groups` role to
  create the UNIX groups used by DebOps during bootstrapping.

- Remove management of Python packages from the role. The ``bootstrap.yml``
  playbook uses the :ref:`debops.python` role to configure Python support on
  the host.

:ref:`debops.lxc` role
''''''''''''''''''''''

- Remove support for direct LXC container management from the role. This
  functionality is better suited for other tools like :command:`lxc-*` set of
  commands, or the Ansible ``lxc_container`` module which should be used in
  custom playbooks. The 'debops.lxc' role focus should be configuration of LXC
  support on a host.

- Remove custom LXC template support. The LXC containers can be created by the
  normal templates provided by the ``lxc`` package, and then configured using
  DebOps roles as usual.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- The tasks that modified the default ``template1`` database and its schema
  have been removed to make the PostgreSQL installation more compatible with
  applications packaged in Debian that rely on the PostgreSQL service. See the
  relevant commit for more details. Existing installations shouldn't be
  affected.


`debops v0.7.2`_ - 2018-03-28
-----------------------------

.. _debops v0.7.2: https://github.com/debops/debops/compare/v0.7.2...v0.7.2

Fixed
~~~~~

General
'''''''

- Add missing ``python-ldap`` dependency as an APT package in the Dockerfile.


`debops v0.7.1`_ - 2018-03-28
-----------------------------

.. _debops v0.7.1: https://github.com/debops/debops/compare/v0.7.0...v0.7.1

Added
~~~~~

New DebOps roles
''''''''''''''''

- The :ref:`debops.ansible` role: install Ansible on a Debian/Ubuntu host using
  Ansible. The ```debops.debops`` role now uses the new role to install
  Ansible instead of doing it directly.

- The :ref:`debops.apt_mark` role: set install state of APT packages
  (manual/auto) or specify that particular packages should be held in their
  current state.  The role is included in the ``common.yml`` playbook.

- The :ref:`debops.kmod` role: manage kernel module configuration and module
  loading at boot time. This role replaces the ``debops-contrib.kernel_module``
  role.

- The ``debops-contrib.etckeeper`` role has been integrated into DebOps as
  :ref:`debops.etckeeper`. The new role is included in the ``common.yml``
  playbook.

:ref:`debops.ifupdown` role
'''''''''''''''''''''''''''

- The role has new tasks that manage custom hooks in other services. First hook
  is :ref:`ifupdown__ref_custom_hooks_filter_dhcp_options` which can be used to
  selectively apply DHCP options per network interface.

Changed
~~~~~~~

Continuous Integration
''''''''''''''''''''''

- The test suite used on Travis-CI now checks the syntax of the YAML files, as
  well as Python and shell scripts included in the repository. The syntax is
  checked using the :command:`yamllint`, :command:`pycodestyle` and
  :command:`shellcheck` scripts, respectively. Tests can also be invoked
  separately via the :command:`make` command.

:ref:`debops.etherpad` role
'''''''''''''''''''''''''''

- The role can now autodetect and use a PostgreSQL database as a backend
  database for Etherpad.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The role should now correctly detect what Internet Protocols are available on
  a host (IPv4, IPv6) and configure firewall only for the protocols that are
  present.

.. __: https://github.com/diafygi/acme-tiny

:ref:`debops.lxc` role
''''''''''''''''''''''

- The role will now generate the ``lxc-debops`` LXC template script from
  different templates, based on an OS release. This change should help fix the
  issues with LXC container creation on Debian Stretch.

:ref:`debops.pki` role
''''''''''''''''''''''

- The X.509 certificate included in the default ``domain`` PKI realm will now
  have a SubjectAltName wildcard entry for the host's FQDN. This should allow
  for easy usage of services related to a particular host in the cluster over
  encrypted connections, for example host monitoring, service discovery, etc.
  which can be now published in the DNS zone at ``*.host.example.org`` resource
  records.

- The role now supports Let's Encrypt ACMEv2 API via the `acme-tiny`__ Python
  script. The existing PKI realms will need to be re-created or updated for the
  new API to work, new PKI realms should work out of the box. Check the
  :ref:`upgrade_notes` for more details.

:ref:`debops.proc_hidepid` role
'''''''''''''''''''''''''''''''

- The role now uses a static GID ``70`` for the ``procadmins`` group to
  synchronize the access permissions on a host and inside the LXC containers.
  You will need to remount the filesystems, restart services and LXC containers
  that rely on this functionality.

:ref:`debops.sysctl` role
'''''''''''''''''''''''''

- The configuration of the kernel parameters has been redesigned, instead of
  being based on YAML dictionaries, is now based on YAML lists of dictionaries
  and can be easily changed via Ansible inventory. You will need to update your
  inventory for the new changes to take effect, refer to the :ref:`role
  documentation <sysctl__ref_parameters>` for details.

Fixed
~~~~~

General
'''''''

- The :command:`debops` command will now generate the :file:`ansible.cfg`
  configuration file with correct path to the Ansible roles provided with the
  DebOps Python package.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- Fix a long standing bug in the role with Ansible failing during welcome page
  template generation with Jinja2 >= 2.9.4. It was related to `non-backwards
  compatible change in Jinja`__ that modified how variables are processed in
  a loop.

.. __: https://github.com/pallets/jinja/issues/659

Removed
~~~~~~~

Roles removed from DebOps
'''''''''''''''''''''''''

- The ``debops-contrib.kernel_module`` Ansible role has been removed; it was
  replaced by the new :ref:`debops.kmod` Ansible role.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The ``ferm-forward`` hook script in the :file:`/etc/network/if-pre-up.d/`
  directory has been removed (existing instances will be cleaned up). Recent
  changes in the :ref:`debops.ferm` role broke idempotency with the
  :ref:`debops.ifupdown` role, and it was determined that the functionality
  provided by the hook is no longer needed, recent OS releases should deal with
  it adequately.


`debops v0.7.0`_ - 2018-02-11
-----------------------------

.. _debops v0.7.0: https://github.com/debops/debops/compare/v0.6.0...v0.7.0

Added
~~~~~

New DebOps roles
''''''''''''''''

- New Ansible roles have been imported from the ``debops-contrib``
  organization: ``apparmor``, ``bitcoind``, ``btrfs``, ``dropbear_initramfs``,
  ``etckeeper``, ``firejail``, ``foodsoft``, ``fuse``, ``homeassistant``,
  ``kernel_module``, ``kodi``, ``neurodebian``, ``snapshot_snapper``, ``tor``,
  ``volkszaehler``, ``x2go_server``. They are not yet included in the main
  playbook and still need to be renamed to fit with the rest of the
  ``debops.*`` roles.

- The :ref:`debops.sysfs` role: configuration of the Linux kernel attributes
  through the :file:`/sys` filesystem. The role is not enabled by default.

- The :ref:`debops.locales` role: configure localization and
  internationalization on a given host or set of hosts.

- The :ref:`debops.machine` role: manage the :file:`/etc/machine-info` file,
  the :file:`/etc/issue` file and a dynamic MOTD.

- The :ref:`debops.proc_hidepid` role: configure the ``/proc`` ``hidepid=``
  options.

- The :ref:`debops.roundcube` role: manage RoundCube Webmail application.

- The :ref:`debops.prosody` role: configure an xmpp server on a given host.

- The :ref:`debops.sysnews` role: manage System News bulletin for UNIX
  accounts.

Continuous Integration
''''''''''''''''''''''

- DebOps roles and playbooks can now be tested using local or remote
  `GitLab CI <https://about.gitlab.com/>`_ instance, with Vagrant, KVM and LXC
  technologies and some custom scripts.

General
'''''''

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

- DebOps roles and playbooks will be included in the Python packages released
  on PyPI. This will allow for easier installation of DebOps via :command:`pip`
  (no need to download the roles and playbooks separately) as well as simple
  stable releases. The DebOps monorepo can still be installed separately.

:ref:`debops.libvirtd` role
'''''''''''''''''''''''''''

- The role can now detect if nested KVM is enabled in a particular virtual
  machine and install KVM support.

:ref:`debops.nodejs` role
'''''''''''''''''''''''''

- The :ref:`debops.nodejs` role can now install `Yarn <https://yarnpkg.com/>`_
  package manager using its upstream APT repository (not enabled by default).

Changed
~~~~~~~

Continuous Integration
''''''''''''''''''''''

- The project repository is tested using :command:`pycodestyle` for compliance
  with Python's `PEP8 Style Guide <https://pep8.org/>`_.

General
'''''''

- The :command:`debops-update` script will now install or update the DebOps
  monorepo instead of separate ``debops-playbooks`` and DebOps roles git
  repositories. Existing installations shouldn't be affected.

- The :command:`debops` script will now include the DebOps monorepo roles and
  playbooks in the generated :file:`ansible.cfg` configuration. The monorepo
  roles and playbooks are preferred over the old ``debops-playbooks`` ones.

  The script is backwards compatible and should work correctly with or without
  the ``debops-playbooks`` repository and roles installed.

- Improved Python 3 support in the DebOps scripts and throughout the
  playbooks/roles. DebOps should now be compatible with both Python versions.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- The GitLab Runner playbook is moved to the ``agent.yml`` playbook; it will be
  executed at the end of the main playbook and should that way include correct
  information about installed services.

:ref:`debops.gunicorn` role
'''''''''''''''''''''''''''

- Update the role to work correctly on Debian Stretch and newer releases. The
  support for multiple :command:`gunicorn` instances using custom Debian
  scripts has been removed in Debian Stretch, therefore the role replaces it
  with its own setup based on :command:`systemd` instances.

:ref:`debops.nodejs` role
'''''''''''''''''''''''''

- The ``npm`` package has been removed from Debian Stable.  The role will now
  install NPM using the GitHub source, unless upstream NodeJS is enabled, which
  includes its own NPM version.

Removed
~~~~~~~

General
'''''''

- Remove the :file:`ipaddr.py` Ansible filter plugin, it is now included in the
  Ansible core distribution.

``debops.console`` role
'''''''''''''''''''''''

- Remove the ``locales`` configuration from the 'debops.console' role, this
  functionality has been moved to the new 'debops.locales' role. You will need
  to update the Ansible inventory variables to reflect the changes.

- Remove management of the :file:`/etc/issue` and :file:`/etc/motd` files from
  the ``debops.console`` role. That functionality is now available in the
  :ref:`debops.machine` role. You will need to update the Ansible inventory
  variables to reflect the changes.

- Management of the ``/proc`` ``hidepid=`` option has been moved to a new role,
  :ref:`debops.proc_hidepid`. You will need to update the Ansible inventory
  variables to reflect the changes.

- Management of the System News using the ``sysnews`` Debian package has been
  removed from the role; it's now available as a separate :ref:`debops.sysnews`
  Ansible role. You will need to update the Ansible inventory variables related
  to System News due to this changes.


debops v0.6.0 - 2017-10-21
--------------------------

Added
~~~~~

General
'''''''

- Various repositories that comprise the DebOps project have been merged into
  a single monorepo which will be used as the main development repository.
  Check the :command:`git` log for information about older releases of DebOps
  roles and/or playbooks.
