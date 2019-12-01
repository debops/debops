.. _upgrade_notes:

Upgrade notes
=============

This document contains information and notes about any changes that are
required in the Ansible inventory or the IT infrastructure managed by DebOps to
perform the upgrades between different stable releases.


Unreleased
----------


v1.2.0 (2019-12-01)
-------------------

Role configuration changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- In the :ref:`debops.dnsmasq` role, :ref:`dnsmasq__ref_interfaces` variable
  configuration, the ``router_enabled`` parameter has been renamed to the
  ``router_state`` parameter, with changed value type.

- In the :ref:`debops.golang` role, the ``golang__*_packages`` variables are
  used to define Go packages instead of simple list of APT packages, with
  entirely new syntax. Existing roles that rely on these variables might need
  to be updated. See the :ref:`golang__ref_packages` documentation for more
  details.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.gitlab` role has an improved LDAP support that uses the
  :ref:`debops.ldap` role infrastructure. Due to that, some of the default
  variables have been changed:

  +---------------------------------+------------------------------------------+---------------+
  | Old variable name               | New variable name                        | Changed value |
  +=================================+==========================================+===============+
  | ``gitlab_ldap_activedirectory`` | :envvar:`gitlab__ldap_activedirectory`   | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_enable``          | :envvar:`gitlab__ldap_enabled`           | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_basedn``          | :envvar:`gitlab__ldap_base_dn`           | Yes           |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_binddn``          | :envvar:`gitlab__ldap_binddn`            | Yes           |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_domain``          | Removed                                  | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_host``            | :envvar:`gitlab__ldap_host`              | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_label``           | :envvar:`gitlab__ldap_label`             | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_manage``          | Removed                                  | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_method``          | :envvar:`gitlab__ldap_encryption`        | Yes           |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_password``        | :envvar:`gitlab__ldap_bindpw`            | Yes           |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_password_file``   | Removed                                  | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_port``            | :envvar:`gitlab__ldap_port`              | No            |
  +---------------------------------+------------------------------------------+---------------+
  | ``gitlab_ldap_uid``             | :envvar:`gitlab__ldap_account_attribute` | Yes           |
  +---------------------------------+------------------------------------------+---------------+

  The location of the GitLab LDAP account object in the LDAP directory tree
  as well as the object class and its attributes has been changed, see the
  :ref:`debops.gitlab LDAP DIT <gitlab__ref_ldap_dit>` documentation page
  for more details.

  Some of the default configuration options have been changed to better
  integrate GitLab with the LDAP environment managed by DebOps:

  ============================================== ================================== ==============================
  Variable name                                  Old value                          New value
  ============================================== ================================== ==============================
  :envvar:`gitlab__ldap_user_filter`             not defined                         too large; see the variable
  ---------------------------------------------- ---------------------------------- ------------------------------
  :envvar:`gitlab__ldap_label`                   ``ldap.{{ ansible_domain }}``      ``LDAP``
  ============================================== ================================== ==============================

- The :ref:`debops.owncloud` role has an improved LDAP support that uses the
  :ref:`debops.ldap` role infrastructure. Due to that, some of the default
  variables have been changed:

  +----------------------------------+-----------------------------------------+---------------+
  | Old variable name                | New variable name                       | Changed value |
  +==================================+=========================================+===============+
  | ``owncloud__ldap_create_user``   | Removed                                 | No            |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_domain``        | Removed                                 | No            |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_basedn``        | :envvar:`owncloud__ldap_base_dn`        | Yes           |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_conf_map``      | :envvar:`owncloud__ldap_default_config` | Yes           |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_host``          | :envvar:`owncloud__ldap_primary_server` | Yes           |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_password``      | :envvar:`owncloud__ldap_bindpw`         | Yes           |
  +----------------------------------+-----------------------------------------+---------------+
  | ``owncloud__ldap_password_file`` | Removed                                 | No            |
  +----------------------------------+-----------------------------------------+---------------+

  The location of the Nextcloud LDAP account object in the LDAP directory tree
  as well as the object class and its attributes has been changed, see the
  :ref:`debops.owncloud LDAP DIT <owncloud__ref_ldap_dit>` documentation page
  for more details.

  The default connection method used by Nextcloud to connect to the LDAP
  directory has been changed from ``ssl`` to ``tls``.

  The LDAP configuration method was rewritten and now uses custom DebOps filter
  plugins to allow merging of configuration from the role defaults and
  inventory variables. See :ref:`owncloud__ref_ldap_config` for more details.

  Some of the default configuration options have been changed to better
  integrate Nextcloud with the LDAP environment managed by DebOps:

  ============================================== =============================================== ==============================
  Variable name                                  Old value                          New value
  ============================================== =============================================== ==============================
  :envvar:`owncloud__ldap_login_filter`          ``(&(|(objectclass=inetOrgPerson))(uid=%uid))`` too large; see the variable
  ---------------------------------------------- ----------------------------------------------- ------------------------------
  :envvar:`owncloud__ldap_group_filter`          ``(&(|(objectclass=posixGroup)))``              too large; see the variable
  ---------------------------------------------- ----------------------------------------------- ------------------------------
  :envvar:`owncloud__ldap_group_assoc_attribute` ``memberUid``                                   ``member``
  ============================================== =============================================== ==============================

  Support for the :ref:`memberOf overlay <slapd__ref_memberof_overlay>` has
  also been enabled by default, since the overlay is included in
  :ref:`debops.slapd` role.

- In the :ref:`debops.ferm` role, some of the connection tracking parameters
  have been renamed:

  +-------------------------+----------------------------------+---------------+
  | Old parameter name      | New parameter name               | Changed value |
  +=========================+==================================+===============+
  | ``item.active_target``  | ``item.tracking_active_target``  | No            |
  +-------------------------+----------------------------------+---------------+
  | ``item.invalid_target`` | ``item.tracking_invalid_target`` | No            |
  +-------------------------+----------------------------------+---------------+
  | ``item.module``         | ``item.tracking_module``         | No            |
  +-------------------------+----------------------------------+---------------+

  See :ref:`ferm__ref_type_connection_tracking` for more details about
  connection tracking.


v1.1.0 (2019-08-25)
-------------------

GPG key management changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`debops.keyring` centralizes management of the APT keyring and various
GPG keyrings in unprivileged UNIX accounts. Various DebOps roles have been
modified to use this role instead of performing the GPG key management on their
own. If you use custom Ansible playbooks with these roles, you will need to
update them to include the :ref:`debops.keyring` role.

List of modified DebOps roles:

- :ref:`debops.ansible`
- :ref:`debops.cran`
- :ref:`debops.docker_registry`
- :ref:`debops.docker_server`
- :ref:`debops.elastic_co`
- :ref:`debops.gitlab_runner`
- :ref:`debops.hashicorp`
- ``debops.hwraid``
- :ref:`debops.icinga`
- :ref:`debops.mariadb`
- :ref:`debops.mariadb_server`
- :ref:`debops.mosquitto`
- :ref:`debops.nginx`
- :ref:`debops.nodejs`
- :ref:`debops.owncloud`
- :ref:`debops.php`
- :ref:`debops.postgresql`
- :ref:`debops.postgresql_server`
- :ref:`debops.rstudio_server`
- :ref:`debops.salt`
- :ref:`debops.yadm`
- ``debops-contrib.bitcoind``
- ``debops-contrib.neurodebian``
- ``debops-contrib.x2go_server``

NodeJS and NPM changes
~~~~~~~~~~~~~~~~~~~~~~

- By default, the :ref:`debops.nodejs` role will install the NodeJS and NPM
  packages from the OS (Debian or Ubuntu) repositories. On the Debian Oldstable
  release (currently Stretch), the packages backported from the Stable release
  will be used. The role supports an automatic upgrade to the upstrean NodeJS
  package when the support for NodeSource repositories is enabled using the
  :envvar:`nodejs__node_upstream` variable.

  On existing installations, status of the upstream APT repositorie should be
  preserved, however note that the Ansible local fact name that tracks this has
  been changed to ``ansible_local.nodejs.node_upstream``, along with the
  default variable name. You might want to update the Ansible inventory to
  reflect the desired status of the NodeJS and NPM upstream support.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.rsnapshot` role has been redesigned and all of its
  ``rsnapshot_*`` variables have been renamed to ``rsnapshot__*`` to contain
  them in their own namespace. You will have to update your inventory.

  The configuration of the hosts to back up has also been redesigned; the role
  does not use Ansible inventory groups to define the hosts to back up
  implicitly; you now have to explicitly specify hosts to back up using the
  :ref:`rsnapshot__ref_hosts` variables. There is a way to replocate the
  previous usage of inventory groups to define hosts to back up as well, see
  the provided examples.

- The ``debops.docker`` role has been renamed to :ref:`debops.docker_server`.
  The ``docker__*`` variables have been renamed to ``docker_server__*``. You
  will have to update your inventory variables and move all hosts to the new
  inventory group ``[debops_service_docker_server]`` to continue using this
  role.

  Also, the Docker server no longer listens on a TCP port by default, even if
  :ref:`debops.pki` is enabled. You must set ``docker_server__tcp`` to ``True``
  and configure an IP address whitelist in ``docker_server__tcp_allow`` if you
  want to connect to the Docker server over a network. It is recommended to use
  :ref:`debops.pki` to secure the connection with TLS.

- The :ref:`debops.lxc` role uses different names of the container
  configuration options depending on the LXC version used on the host. The
  ``name`` parameters used in the configuration might change unexpectedly
  between LXC versions, which might lead to wrong configuration entries being
  merged and broken LXC configuration.

  If you have configured :ref:`lxc__ref_configuration` variables in the Ansible
  inventory, review them before applying the role configuration on LXC hosts.
  You can check the :envvar:`lxc__default_configuration` variable to see which
  ``name`` parameters can change.

- The ``lxc__net_interface_fqdn`` variable has been renamed to
  :envvar:`lxc__net_fqdn` to conform to the variable naming scheme for domain
  and FQDN names used in different DebOps roles. The new variable defines the
  FQDN name of the ``lxcbr0`` interface. The :envvar:`lxc__net_domain` variable
  which has done that previously is now used to define the DNS domain for the
  internal LXC subnet, and the new :envvar:`lxc__net_base_domain` variable
  defines the base DNS domain for the ``lxc.`` subdomain.

- The :ref:`debops.ipxe` role default variables have been renamed to move them
  to their own ``ipxe__*`` namespace; you will have to update the Ansible
  inventory.

- The ``core__keyserver`` variable and its corresponding local fact have been
  replaced by the :envvar:`keyring__keyserver` with a corresponding local fact.

- The :ref:`debops.nginx` role no longer defaults to limiting the allowed HTTP
  request methods to GET, HEAD and POST on PHP-enabled websites. Use the
  ``item.php_limit_except`` parameter if you want to keep limiting the request
  methods.

- The ``nodejs__upstream*`` variables in the :ref:`debops.nodejs` role have
  been renamed to ``nodejs__node_upstream*`` to better indicate their purpose
  and differentiate them from the ``nodejs__yarn_upstream*`` variables.

- The ``dokuwiki__main_domain`` variable has been renamed to
  :envvar:`dokuwiki__fqdn` to fit the naming scheme in other DebOps roles.


v1.0.0 (2019-05-22)
-------------------

Redesigned OpenLDAP support
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.slapd` role has been redesigned from the ground up,
  everything is new. Existing OpenLDAP servers/clusters will break if the new
  role is applied on them, don't do it. Set up a new OpenLDAP server/cluster
  and import the LDAP directory afterwards. See the role documentation for more
  details.

Changes to the UNIX group and account management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.users` Ansible role has been modernized and it now uses the
  custom Ansible filter plugins included in DebOps to manage the UNIX groups
  and accounts. The group and account management now uses the same merged list
  of entries, which means that two new parameters have been added to control
  when groups or accounts are created/removed. You might need to update your
  inventory configuration if you use the role to create UNIX groups without
  corresponding accounts, or you put UNIX accounts in shared primary groups.

  By default, :ref:`debops.users` will create user private groups if
  ``item.group`` parameter is not specified; if you want to add accounts to the
  ``users`` primary group, you need to specify it explicitly.

  The ``user`` parameter can be used to disable the account management, so that
  only UNIX group is created. The ``private_group`` parameter controls the
  management of the UNIX group for a given configuration entry. See the role
  documentation for more details.

- The ``users__default_system`` variable has been removed from the
  :ref:`debops.users` role. The UNIX groups and accounts created by the role on
  hosts with the LDAP support will be normal accounts, not "system" accounts,
  and will use UID/GID >= 1000. This can be controlled per-user/per-group using
  the ``item.system`` parameter.

- The ``item.createhome`` parameter has been renamed to ``item.create_home`` in
  accordance with the renamed parameter of the ``user`` Ansible module.

- The ``users__resources``, ``users__group_resources`` and
  ``users__host_resources`` variables have been removed. Their functionality
  has been reimplemented as the ``item.resources`` parameter of the
  ``users__*_accounts`` variables. See the role documentation for more details.

- The management of the admin accounts has been removed from the
  :ref:`debops.users` role and is now done in the :ref:`debops.system_users`
  role. See the :envvar:`system_users__default_accounts` for a list of the
  default admin accounts created on the remote hosts.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.phpipam` has been refactored. Now the variables have been
  renamed from ``phpipam_*`` to ``phpipam__*``

- The :ref:`debops.auth` default variables related to LDAP client configuration
  have been removed; the functionality is now managed by the
  :ref:`debops.ldap`, :ref:`debops.nslcd` and :ref:`debops.nsswitch` Ansible
  roles. The table below shows the old variable names and their new
  equivalents:

  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | Old variable name                                | New variable name                | Changed value                                    |
  +==================================================+==================================+==================================================+
  | ``auth_ldap_conf``                               | :envvar:`ldap__enabled`          | ``False`` by default                             |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_domain``                        | :envvar:`ldap__domain`           | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_hostdn``                        | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_uri``                           | :envvar:`ldap__servers_uri`      | Based on DNS SRV records                         |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_tls_cacert``                    | Removed                          | In :envvar:`ldap__default_configuration`         |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_tls_reqcert``                   | Removed                          | In :envvar:`ldap__default_configuration`         |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_ldap_conf_options``                       | Removed                          | In :envvar:`ldap__default_configuration`         |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nsswitch``                                | Removed                          | Replaced by :ref:`debops.nsswitch`               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_conf``                              | Removed                          | Replaced by :ref:`debops.nslcd`                  |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_domain``                            | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_ldap_server``                       | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_uri``                               | Removed                          | In :envvar:`nslcd__default_configuration`        |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_base``                              | :envvar:`nslcd__ldap_base_dn`    | Based on :ref:`debops.ldap` facts                |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_tls_reqcert``                       | Removed                          | In :envvar:`nslcd__default_configuration`        |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_tls_cacertfile``                    | Removed                          | In :envvar:`nslcd__default_configuration`        |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_basedn``                  | :envvar:`nslcd__ldap_device_dn`  | Based on :ref:`debops.ldap` facts                |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_cn``                      | :envvar:`nslcd__ldap_self_rdn`   | Yes, different attribute, different value source |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_dn``                      | :envvar:`nslcd__ldap_binddn`     | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_basepw``                  | :envvar:`nslcd__ldap_bindpw`     | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_password``                | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_bind_host_hash``                    | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_password_length``                   | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_options``                           | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_nss_min_uid``                       | Removed                          | In :envvar:`nslcd__default_configuration`        |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_pam_mkhomedir_umask``                     | :envvar:`nslcd__mkhomedir_umask` | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_pam_authz_search``                  | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_pam_authz_search_host``             | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_pam_authz_search_service``          | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+
  | ``auth_nslcd_pam_authz_search_host_and_service`` | Removed                          | No                                               |
  +--------------------------------------------------+----------------------------------+--------------------------------------------------+

- The :envvar:`sshd__default_allow_groups` default variable has been changed to
  an empty list. The group-based access control has been moved to a PAM access
  control rules defined in the :envvar:`sshd__pam_access__dependent_rules`
  variable.

  Access to the OpenSSH service by the ``admins``, ``sshusers`` and
  ``sftponly`` UNIX groups members should work the same as before. Access to
  the ``root`` account has been limited to hosts in the same DNS domain. UNIX
  accounts not in the aforementioned UNIX groups can access the OpenSSH service
  from hosts in the same DNS domain (other restrictions like public key
  presence still apply). See :ref:`debops.pam_access` documentation for more
  details about defining the PAM access rules.

- The default variables in the :ref:`debops.sshd` role related to LDAP support
  have been modified:

  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | Old variable name                           | New variable name              | Changed value                                    |
  +=============================================+================================+==================================================+
  | :envvar:`sshd__authorized_keys_lookup`      | Not modified                   | Based on :ref:`debops.ldap` facts                |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | :envvar:`sshd__authorized_keys_lookup_user` | Not modified                   | Yes, to ``sshd``                                 |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__authorized_keys_lookup_group``      | Removed                        | No                                               |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__authorized_keys_lookup_home``       | Removed                        | No                                               |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | :envvar:`sshd__authorized_keys_lookup_type` | Not modified                   | Yes, ``sss`` included by default                 |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_domain``                       | Removed                        | No                                               |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_base``                         | :envvar:`sshd__ldap_base_dn`   | Based on :ref:`debops.ldap` facts                |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_bind_basedn``                  | :envvar:`sshd__ldap_device_dn` | Based on :ref:`debops.ldap` facts                |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_bind_cn``                      | :envvar:`sshd__ldap_self_rdn`  | Yes, different attribute, different value source |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_bind_dn``                      | :envvar:`sshd__ldap_binddn`    | Yes                                              |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_bind_bind_pw``                 | :envvar:`sshd__ldap_bindpw`    | Yes, different password path                     |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_bind_basepw``                  | Removed                        | No                                               |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+
  | ``sshd__ldap_password_length``              | Removed                        | No                                               |
  +---------------------------------------------+--------------------------------+--------------------------------------------------+

- The management of the ``root`` account dotfiles has been removed from the
  :ref:`debops.users` role and is now included in the
  :ref:`debops.root_account` role. The dotfiles are managed using
  :command:`yadm` script, installed by the :ref:`debops.yadm` role. The
  ``users__root_accounts`` list has been removed.


v0.8.1 (2019-02-02)
-------------------

Subordinate UID/GID ranges for root
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.root_account` role will register a set of UID/GID ranges for
  the ``root`` account in the :file:`/etc/subuid` and :file:`/etc/subgid`
  databases.  Depending on the OS distribution and release, these databases
  might contain existing UID/GID ranges which might interfere with the default
  set of 100000-165536 UID/GID range selected for the ``root`` account.

  In that case you should either disable this functionality, or recreate the
  host, at which point the UID/GID ranges for ``root`` will be reserved first,
  and any new accounts created by the system will use subsequent UIDs/GIDs.
  You can also update the UID/GID ranges manually, or select different UID/GID
  ranges for the ``root`` account in the role defaults.

Changes to Redis support in GitLab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The Redis support has been removed from the :ref:`debops.gitlab` playbook.
  Since GitLab still requires Redis to work properly, you need to enable
  :ref:`debops.redis_server` role explicitly for the GitLab host. GitLab
  installation instructions have been updated to reflect this fact.

- To manage Redis on existing GitLab installations, you should enable the
  :ref:`debops.redis_server` role on them and run the Redis and GitLab
  playbooks afterwards. The existing Redis instance will be stopped and new
  Redis instance will be set up, with the same TCP port and password. Since the
  database will be empty, Gitaly service might stop working. After running the
  Redis Server and GitLab playbooks, restart the entire GitLab slice to
  re-populate Redis. You might expect existing GitLab sessions to be invalid
  and users to have to log in again.

- The :ref:`debops.redis_server` role will configure APT preferences on Debian
  Stretch to install Redis from the ``stretch-backports`` repository. The
  playbook run on existing installations will not upgrade the packages
  automatically, but you might expect it on normal system upgrade.

Changes related to packet forwarding in firewall and sysctl
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.ifupdown` role now uses :ref:`debops.sysctl` role directly
  as a dependency to generate forwarding configuration for each managed network
  interface that has it enabled. This might impact packet forwarding on
  existing systems; run the role with Ansible ``--diff --check`` options first
  to review the planned changes to the host.

- The :ref:`debops.ferm` role will no longer enable packet forwarding on all
  network interfaces. Existing :file:`/etc/sysctl.d/30-ferm.conf` configuration
  file can be removed using the :ref:`debops.debops_legacy` role.

  The :ref:`debops.ferm` role will remove firewall rules that enabled
  forwarding between "external" and "internal" network interfaces, named
  ``forward_external_in``, ``forward_external_out`` and ``forward_internal``.
  They are redundant with the similar firewall rules generated by the
  :ref:`debops.ifupdown` role and their removal shouldn't impact connectivity,
  however you should check the modifications to the firewall just in case.

Redesigned DNSmasq support
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.dnsmasq` role has been redesigned from the ground up. The
  configuration is now merged from multiple sources (role defaults, Ansible
  inventory), role defines separate subdomains for each of the network
  interfaces, and automatically enables support for local Consul DNS service or
  LXC subdomain if they are detected on the host.

- Most of the ``dnsmasq__*`` default variables that defined the
  :command:`dnsmasq` configuration have been removed. Their functionality is
  exposed either as parameters of network interface configuration, or can be
  easily changed via the main configuration pipeline. See the documentation of
  :ref:`dnsmasq__ref_configuration` or :ref:`dnsmasq__ref_interfaces` for more
  details. If you use DNSmasq on a host managed by DebOps, you will have to
  modify your Ansible inventory.

- The generated :command:`dnsmasq` configuration has been split from a single
  ``00_main.conf`` configuration file into multiple separate files stored in
  the :file:`/etc/dnsmasq.d/` directory. The old ``00_main.conf`` configuration
  file will be automatically removed if found, to avoid issues with duplicated
  configuration options.

- The role provides an easy to use way to define DHCP clients with IP address
  reservation, as well as DNS resource records. See
  :ref:`dnsmasq__ref_dhcp_dns_entries` documentation for examples and more
  details.

- The configuration of TCP Wrappers for the TFTP service has been removed from
  the :ref:`debops.dnsmasq` role, and is now done via the
  :ref:`debops.tcpwrappers` Ansible role and its dependent variables.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.grub` role was redesigned, most of the ``grub_*`` default
  variables have been removed and the new configuration method has been
  implemented. The role variables have been namespaced, the role now uses
  ``grub__*`` variabe naming scheme. Check the role documentation for details
  about configuring GRUB via Ansible inventory.

- Variables related to :command:`dhcp_probe` in the :ref:`debops.dhcpd` role
  have been replaced with the variables from the :ref:`debops.dhcp_probe` role.
  They are now namespaced and mostly with the same value types.

  The new :ref:`debops.dhcp_probe` role utilizes :command:`systemd` templated
  instances, and might not work correctly on older Debian/Ubuntu releases.

- The variables related to packet forwarding in the :ref:`debops.ferm` role
  and related roles have been removed:

  - ``ferm__forward``
  - ``ferm__forward_accept``
  - ``ferm__external_interfaces``
  - ``ferm__internal_interfaces``
  - ``libvirtd__ferm__forward``
  - ``lxc__ferm__forward``

  The related Ansible local fact ``ansible_local.ferm.forward`` has also been
  removed.

  You can use the :ref:`debops.ifupdown` role to configure packet forwarding
  per network interface, in the firewall as well as via the kernel parameters.

- Host and domain management has been removed from the ``debops.bootstrap``
  role. This functionality is now done via the :ref:`debops.netbase` role,
  included in the bootstrap playbook. Some of the old variables have their new
  equivalents:

  +-----------------------------------------------+--------------------------------------------+---------------+
  | Old variable name                             | New variable name                          | Changed value |
  +===============================================+============================================+===============+
  | ``bootstrap__hostname_domain_config_enabled`` | :envvar:`netbase__hostname_config_enabled` | No            |
  +-----------------------------------------------+--------------------------------------------+---------------+
  | ``bootstrap__hostname``                       | :envvar:`netbase__hostname`                | No            |
  +-----------------------------------------------+--------------------------------------------+---------------+
  | ``bootstrap__domain``                         | :envvar:`netbase__domain`                  | No            |
  +-----------------------------------------------+--------------------------------------------+---------------+
  | ``bootstrap__etc_hosts``                      | Removed                                    | No            |
  +-----------------------------------------------+--------------------------------------------+---------------+
  | ``bootstrap__hostname_v6_loopback``           | Removed                                    | No            |
  +-----------------------------------------------+--------------------------------------------+---------------+

  Support for configuring IPv6 loopback address has been removed entirely. This
  was required when some of the DebOps roles relied on the ``ansible_fqdn``
  value for task delegation between hosts. Since then, task delegation has been
  updated to use the ``inventory_hostname`` values and ensuring that the IPv6
  loopback address resolves to a FQDN address of the host is no longer
  required.

- The ``netbase__*_hosts`` variables in the :ref:`debops.netbase` role have
  been redesigned to use YAML lists instead of dictionaries. See
  :ref:`netbase__ref_hosts` for more details.

- The ``resources__group_name`` variable has been removed in favor of using
  all the groups the current hosts is in. This change has been reflected in the
  updated variable :envvar:`resources__group_templates`.
  If you need to use a specific group update the :envvar:`resources__group_templates`
  accordingly.
  Read the documentation about :ref:`resources__ref_templates` for more details on
  templating with `debops.resources`.

Changes related to LXC containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.lxc` role will configure new LXC containers to attach to the
  ``lxcbr0`` bridge by default. Existing LXC containers will not be modified.
  You can change the default bridge used on container creation using the
  :ref:`lxc__ref_configuration` variables.

- The :ref:`debops.lxc` role has been updated to use the :command:`systemd`
  ``lxc@.service`` instances to manage the containers instead of using the
  :command:`lxc-*` commands directly. Existing LXC containers should not be
  affected, but it is recommended to switch them under the :command:`systemd`
  control. To do that, you should disable the container autostart in the
  :file:`/var/lib/lxc/<container>/config` configuration files:

  .. code-block:: none

     lxc.start.auto = 0

  This will make sure that the containers are not started by the
  ``lxc.service`` service on boot. Next, after stopping the running containers,
  enable and start the containers via the :command:`systemd` instance:

  .. code-block:: console

     systemctl enable lxc@<container>.service
     systemctl start lxc@<container>.service

  This should ensure that the containers are properly shut down and started
  with the host system.


v0.8.0 (2018-08-06)
-------------------

UNIX account and group configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Configuration of UNIX system groups and accounts included in the ``admins``
  UNIX group has been removed from the :ref:`debops.auth` role. This
  functionality is now done by the :ref:`debops.system_groups` role. The
  variable names and their values changed, see the :ref:`debops.system_groups`
  role documentation for details.

GitLab :command:`gitaly` installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.gitlab` role will now build and install the
  :command:`gitaly` service using unprivileged ``git`` UNIX account instead of
  ``root``. To perform the update correctly, you might need to remove directories

  .. code-block:: console

     /usr/local/src/gitlab/gitlab.com/gitaly.git/
     /var/local/git/gitaly/

  Some files in these directories are owned by ``root`` and that can prevent
  the correct build of the Go binaries. You might also want to stop the
  ``gitlab-gitaly.service`` service and start it afterwards.

  The above steps shouldn't impact new GitLab installations.

UTF8 encoding in MariaDB
~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.mariadb_server` and :ref:`debops.mariadb` roles will now use
  the ``utf8mb4`` character encoding by default. This encoding is `the real
  UTF-8 encoding`__ and not the internal MySQL encoding. This change might
  impact existing MySQL databases; you can read `an UTF-8 conversion guide`__
  to check if your database needs to be converted.

  .. __: https://medium.com/@adamhooper/in-mysql-never-use-utf8-use-utf8mb4-11761243e434
  .. __: https://mathiasbynens.be/notes/mysql-utf8mb4

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The ``console_preferred_editors`` list has been removed, configuration of the
  preferred :command:`vim` editor is now done in the :ref:`debops.apt_install`
  role which also installs it.

- The ``console_custom_files`` variable has been removed along with the
  functionality in ``debops.console`` role. Use the :ref:`debops.resources`
  role variables to copy custom files instead. The role is also included in the
  common playbook, although a bit earlier, which shouldn't impact normal use
  cases.

- The management of the :file:`/etc/hosts` file has been removed from the
  ``debops.console`` role and is now done via the :ref:`debops.netbase` role
  which has to be enabled through the Ansible inventory. The variables have
  been renamed:

  +-------------------------+--------------------------------+---------------+
  | Old variable name       | New variable name              | Changed value |
  +=========================+================================+===============+
  | ``console_hosts``       | :envvar:`netbase__hosts`       | No            |
  +-------------------------+--------------------------------+---------------+
  | ``console_group_hosts`` | :envvar:`netbase__group_hosts` | No            |
  +-------------------------+--------------------------------+---------------+
  | ``console_host_hosts``  | :envvar:`netbase__host_hosts`  | No            |
  +-------------------------+--------------------------------+---------------+

- Configuration of the APT autoremove options has been moved from the
  :ref:`debops.apt` role to the :ref:`debops.apt_mark` role, because the latter
  role has more specific scope. The variable names as well as their default
  values have been changed to correctly reflect the meaning of the
  corresponding APT configuration options:

  +--------------------------------+-----------------------------------------------------+------------------+
  | Old variable name              | New variable name                                   | Changed value    |
  +================================+=====================================================+==================+
  | ``apt__autoremove_recommends`` | :envvar:`apt_mark__autoremove_recommends_important` | Yes, to ``True`` |
  +--------------------------------+-----------------------------------------------------+------------------+
  | ``apt__autoremove_suggests``   | :envvar:`apt_mark__autoremove_suggests_important`   | Yes, to ``True`` |
  +--------------------------------+-----------------------------------------------------+------------------+

  By default the APT packages installed via Recommends or Suggests dependencies
  will not be considered for autoremoval. If the user sets any package
  configuration via :ref:`debops.apt_mark` role, the autoremoval will be
  enabled automatically.

- The ``bootstrap__sudo`` and ``bootstrap__sudo_group`` variables have been
  removed from the ``debops.bootstrap`` role. The ``bootstrap.yml`` playbook
  now uses the :ref:`debops.sudo` role to configure :command:`sudo` service on
  a host, use its variables instead to control the service in question.

- The ``bootstrap__admin_groups`` variable will now use list of UNIX
  groups with ``root`` access defined by the :ref:`debops.system_groups` via
  Ansible local facts.

- The contents of the :envvar:`sshd__allow_groups` variable have been moved to
  the new :envvar:`sshd__default_allow_groups` variable. The new variable also
  uses the :ref:`debops.system_groups` Ansible local facts as a data source.

- The ``bootstrap__raw`` and ``bootstrap__mandatory_packages`` variables have
  been removed. See the :ref:`debops.python` role documentation for their
  equivalents.

- The ``apt_install__python_packages`` variable has been removed from the
  :ref:`debops.apt_install` role. Use the :ref:`debops.python` Ansible role to
  install Python packages.

- The ``nodejs__upstream_version`` variable has been renamed to
  :envvar:`nodejs__node_upstream_release` to better represent the contents,
  which is not a specific NodeJS version, but a specific major release.

- The ``gitlab_domain`` variable, previously used to set the FQDN of the GitLab
  installation, now only sets the domain part; it's value is also changed from
  a YAML list to a string.

  The :envvar:`gitlab__fqdn` variable is now used to set the GitLab FQDN and
  uses the ``gitlab_domain`` value as the domain part.


v0.7.2 (2018-03-28)
-------------------

No changes.


v0.7.1 (2018-03-28)
-------------------

X.509 certificate changes
~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.pki` role now generates the default X.509 certificate for
  the ``domain`` PKI realm with a wildcard entry for the host's FQDN (for
  example, ``*.host.example.org``). This will be true by default on new hosts
  introduced to the cluster; if you want your old hosts to have the new X.509
  certificates, you need to recreate the ``domain`` PKI realm by removing the
  :file:`/etc/pki/realms/domain/` directory on the remote hosts and re-running
  the :ref:`debops.pki` role against them.

  The change is done in the :envvar:`pki_default_realms` variable, if you
  redefined it in the Ansible inventory, you might want to update your version
  to include the new SubjectAltName entry.

- The latest :program:`acme-tiny` Python script uses ACMEv2 API by default, and
  the :ref:`debops.pki` role is now compatible with the upstream changes. The
  ACME certificates should work out of the box in new PKI realms, after the
  :program:`acme-tiny` installation is updated.

  The existing PKI realms will stop correctly regenerating Let's Encrypt
  certificates, because their configuration is not updated automatically by the
  role. The presence of the :file:`acme/error.log` file will prevent the
  :program:`acme-tiny` script from requesting the certificates to not trip the
  Let's Encrypt rate limits.

  Easiest way to fix this is to remove the entire PKI realm
  (:file:`/etc/pki/realms/*/` directory) and re-run the :ref:`debops.pki` role
  against the host. The role will create a new PKI realm based on the previous
  configuration and ACME certificates should start working again.  Services
  like :program:`nginx` that have hooks in the :file:`/etc/pki/hooks/`
  directory should be restarted automatically, you might need to manually
  restart other services as needed.

  Alternatively, you can update the Let's Encrypt API URL in the realm's
  :file:`config/realm.conf` file by replacing the line:

  .. code-block:: bash

     config['acme_ca_api']='https://acme-v01.api.letsencrypt.org'

  with:

  .. code-block:: bash

     config['acme_ca_api']='https://acme-v02.api.letsencrypt.org/directory'

  This should tell the :program:`pki-realm` script to send requests for new
  certificates to the correct URL. You still need to run the :ref:`debops.pki`
  role against the host to install the updated :program:`pki-realm` script and
  update the :program:`acme-tiny` script.

Role changes
~~~~~~~~~~~~

- The :ref:`debops.debops` role now uses the :ref:`debops.ansible` role to
  install Ansible instead of doing it by itself. The relevant code has been
  removed, see the :ref:`debops.ansible` role documentation for new variables.

- The ``debops-contrib.kernel_module`` role has been replaced by the
  :ref:`debops.kmod` role. All of the variable names have been changed, as well
  as their usage. See the documentation of the new role for more details.

- The :ref:`debops.proc_hidepid` role was modified to use a static GID ``70``
  for the ``procadmins`` group to allow synchronization between host and LXC
  containers on that host. The role will apply changes in the
  :file:`/etc/fstab` configuration file, but it will not change existing
  :file:`/proc` mount options. You need to remount the filesystem manually,
  with a command:

  .. code-block:: console

     ansible all -b -m command -a 'mount -o remount /proc'

  The :file:`/proc` filesystem mounted inside of LXC containers cannot be
  remounted this way, since it's most likely mounted by the host itself. You
  will need to check the LXC container configuration in the
  :file:`/var/lib/lxc/*/config` files and update the mount point options to use
  the new static GID. Restart the LXC container afterwards to remount the
  :file:`/proc` filesystem.

  You will also need to restart all services that rely on the ``procadmins``
  group, for example :command:`snmpd`, to activate the new GID.

- The :ref:`debops.sysctl` configuration has been redesigned. The role now uses
  YAML lists instead of YAML dictionaries as a base value of the
  ``sysctl__*_parameters`` default variables. The kernel parameter
  configuration format has also been changed to be easy to override via Ansible
  inventory. Role can now configure multiple files in :file:`/etc/sysctl.d/`
  directory. Refer to the role documentation for details.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :ref:`debops.netbox` role has been updated, some variable names were
  changed:

  +------------------------------------+------------------------------------------+---------------+
  | Old variable name                  | New variable name                        | Changed value |
  +------------------------------------+------------------------------------------+---------------+
  | ``netbox__config_netbox_username`` | :envvar:`netbox__config_napalm_username` | No            |
  +------------------------------------+------------------------------------------+---------------+
  | ``netbox__config_netbox_password`` | :envvar:`netbox__config_napalm_password` | No            |
  +------------------------------------+------------------------------------------+---------------+

- The variables that specify files to ignore in the new :ref:`debops.etckeeper`
  role have been renamed from their old versions in
  ``debops-contrib.etckeeper`` role, and their value format changed as well.
  See the documentation of the new role for details.


v0.7.0 (2018-02-11)
-------------------

This is mostly a maintenance release, dedicated to reorganization of the DebOps
:command:`git` repository and expanding documentation.

Role changes
~~~~~~~~~~~~

- The :ref:`debops.nodejs` role now installs NPM using a script in upstream
  :command:`git` repository. This might cause issues with already installed NPM
  package, because of that it will be automatically removed by the role if
  found. You should verify that the role behaves correctly on existing systems
  before applying it in production.

- The :ref:`debops.gunicorn` role has rewritten configuration model based on
  :command:`systemd` instanced units. The existing configuration shouldn't
  interfere, however you might need to update the Ansible inventory
  configuration variables to the new syntax.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The localization configuration previously located in the ``debops.console``
  role is now located in the :ref:`debops.locales` role. List of default
  variables that were affected:

  +-----------------------------+---------------------------------+---------------+
  | Old variable name           | New variable name               | Changed value |
  +=============================+=================================+===============+
  | ``console_locales``         | :envvar:`locales__default_list` | No            |
  +-----------------------------+---------------------------------+---------------+
  | ``console_locales_default`` | :envvar:`locales__system_lang`  | No            |
  +-----------------------------+---------------------------------+---------------+

  There are also new localization variables for :envvar:`all hosts <locales__list>`,
  :envvar:`group of hosts <locales__group_list>`, :envvar:`specific hosts <locales__host_list>`
  and :envvar:`dependent roles <locales__dependent_list>`.

- The :file:`/etc/issue` and :file:`/etc/motd` configuration has been removed
  from the ``debops.console`` role and is now done by the :ref:`debops.machine`
  role. List of default variables that were affected:

  +-------------------+---------------------------------+---------------+
  | Old variable name | New variable name               | Changed value |
  +===================+=================================+===============+
  | ``console_issue`` | :envvar:`machine__organization` | No            |
  +-------------------+---------------------------------+---------------+
  | ``console_motd``  | :envvar:`machine__motd`         | No            |
  +-------------------+---------------------------------+---------------+

  The support for dynamic MOTD has been implemented by the :ref:`debops.machine`
  role, you might want to use that instead of the static MOTD file.

- Configuration of the ``/proc`` ``hidepid=`` option has been removed from the
  ``debops.console`` and is now available in the new :ref:`debops.proc_hidepid`
  Ansible role. List of default variables that were affected:

  +--------------------------------+---------------------------------+---------------+
  | Old variable name              | New variable name               | Changed value |
  +================================+=================================+===============+
  | ``console_proc_hidepid``       | :envvar:`proc_hidepid__enabled` | No            |
  +--------------------------------+---------------------------------+---------------+
  | ``console_proc_hidepid_level`` | :envvar:`proc_hidepid__level`   | No            |
  +--------------------------------+---------------------------------+---------------+
  | ``console_proc_hidepid_group`` | :envvar:`proc_hidepid__group`   | No            |
  +--------------------------------+---------------------------------+---------------+

  The logic to enable/disable the ``hidepid=`` configuration has been moved to
  the :envvar:`proc_hidepid__enabled` variable to be more accessible. The role
  creates its own set of Ansible local facts with new variable names, you might
  need to update configuration of the roles that relied on them.

- Configuration of the ``sysnews`` package has been removed from the
  ``debops.console`` role, it's now available in the :ref:`debops.sysnews`
  Ansible role. There were extensive changes in the variable names and
  parameters, read the documentation of the new role for details.


v0.6.0 (2017-10-21)
-------------------

This is an initial release based off of the previous DebOps roles, playbooks
and tools located in separate :command:`git` repositories. There should be no
changes needed between the old and the new infrastructure and inventory.
