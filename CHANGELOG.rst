.. _changelog:

Changelog
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <https://keepachangelog.com/en/1.0.0/>`__.

This file contains only general overview of the changes in the DebOps project.
The detailed changelog can be seen using :command:`git log` command.

You can read information about required changes between releases in the
:ref:`upgrade_notes` documentation.


`debops stable-1.2`_ - unreleased
---------------------------------

.. _debops stable-1.2: https://github.com/debops/debops/compare/v1.2.0...stable-1.2

Added
~~~~~

:ref:`debops.fail2ban` role
'''''''''''''''''''''''''''

- The :command:`fail2ban` service will by default use the hostnames from logs
  to lookup IP addresses via DNS, but will warn about it. You can change this
  behaviour via the :envvar:`fail2ban_usedns` variable.

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- The custom patches applied by the role can now be reverted conditionally.

:ref:`debops.gunicorn` role
'''''''''''''''''''''''''''

- Add the :ref:`debops.secret` role as a dependency to allow usage of the
  confidential values.

:ref:`debops.php` role
''''''''''''''''''''''

- Ensure that the PHP support works on Ubuntu Focal.

:ref:`debops.pki` role
''''''''''''''''''''''

- The role can now instruct acme-tiny to register an ACME account with one or
  more contact URLs. Let's Encrypt for example uses this information to notify
  you about expiring certificates and emergency revocation.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- Allow selection of the day of the month for monthly backups.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Buster netboot installer version
  has been updated to the next point release, 10.4.

Continuous Integration
''''''''''''''''''''''

- The Vagrant provisioning script will install Ansible from PyPI by default.
  The version included in the current Debian Stable (Buster) is too old for the
  DebOps playbooks and roles.

- Various improvements in the Vagrant box environment have been backported from
  the ``master`` branch.

General
'''''''

- In new DebOps environments, Ansible will ignore any missing inventory groups
  using the ``host_pattern_mismatch`` parameter. This will disable the "Could
  not match supplied host pattern" warning message present in most of the
  playbooks included in DebOps. To disable this message in an existing
  environment, add in the :file:`.debops.cfg` configuration file:

  .. code-block:: ini

     [ansible inventory]
     host_pattern_mismatch = ignore

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- The GitLab package repository signing key has been replaced with the new key
  that has been in use since 2020-04-06, allowing APT to update package lists
  again. See the `GitLab.com blog`__ for more information about this change.

  .. __: https://about.gitlab.com/releases/2020/03/30/gpg-key-for-gitlab-package-repositories-metadata-changing/

:ref:`debops.mcli` role
'''''''''''''''''''''''

- The Ansible fact script has been updated to new MinIO Client version syntax.

:ref:`debops.minio` role
''''''''''''''''''''''''

- The Ansible fact script has been updated to new MinIO Server version syntax.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- TLSv1.3 is now enabled by default for nginx version 1.13.0 and up.

Fixed
~~~~~

General
'''''''

- Correctly display shell error messages in the :command:`debops-defaults`
  script.

:ref:`debops.cron` role
'''''''''''''''''''''''

- Fix idempotency issue in the :file:`/etc/crontab` file.

- Fix creation of empty environment variables in :command:`cron` configuration
  files managed by Ansible.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- Use correct ``bin_dir`` path in Gitaly configuration file.

:ref:`debops.golang` role
'''''''''''''''''''''''''

- Fix Ansible local fact script compatibility with Python 3.x environment.

:ref:`debops.minio` role
''''''''''''''''''''''''

- Fix an issue during installation of recent MinIO releases, where during an
  initial restart the MinIO service would switch into "safe mode" when
  a problem with configuration is detected; this would prevent the service to
  be restarted correctly. Now the service should be properly stopped by
  :command:`systemd` after a stop timeout.

:ref:`debops.mosquitto` role
''''''''''''''''''''''''''''

- Ignore the ``group`` and ``mode`` parameters defined in the Mosquitto bridge
  configuration; they are used to specify the configuration file attributes.

:ref:`debops.nginx` role
''''''''''''''''''''''''

- The role now always sets the HTTP Strict Transport Security header when it is
  enabled, regardless of the response code.

- The role tasks have been reordered to fix an idempotency issue in the
  :command:`nginx` configuration files.

:ref:`debops.nsswitch` role
'''''''''''''''''''''''''''

- Fix idempotency issue in the role fact script.

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- Don't lookup the ``_smtp._tcp`` SRV resource records using the ``dig``
  Ansible lookup plugin if the ``ansible_domain`` variable is empty.

:ref:`debops.owncloud` role
'''''''''''''''''''''''''''

- The ``file`` Ansible module does not support the ``validate`` parameter; it
  seems that this was a copying mistake and has been removed.


`debops v1.2.3`_ - 2020-02-24
-----------------------------

.. _debops v1.2.3: https://github.com/debops/debops/compare/v1.2.2...v1.2.3

Added
~~~~~

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- The role can now manage PostgreSQL log files in a separate, custom directory.

:ref:`debops.resources` role
''''''''''''''''''''''''''''

- Add support for the ``access_time`` and ``modification_time`` parameters of
  the Ansible file module to the role.

Changed
~~~~~~~

Updates of upstream application versions
''''''''''''''''''''''''''''''''''''''''

- In the :ref:`debops.ipxe` role, the Debian Stretch and Debian Buster netboot
  installer versions have been updated to their next point releases, 9.11 and
  10.3 respectively.

General
'''''''

- The :ref:`debops.machine` role is reordered in the file:`common.yml` playbook
  to be executed before the :ref:`debops.ldap` role which uses the former role
  facts. It's also added to the :file:`bootstrap-ldap.yml` playbook for
  completeness.

Fixed
~~~~~

:ref:`debops.ferm` role
'''''''''''''''''''''''

- Fixed incorrect removal of the ferm rule set by :ref:`debops.avahi` on
  IPv6-enabled systems.

:ref:`debops.netbase` role
''''''''''''''''''''''''''

- Use short timeout for DNS queries performed by the Ansible local fact script,
  in case that the DNS infrastructure is not configured. This avoids 60s
  timeouts during Ansible fact gathering in such cases.

:ref:`debops.nslcd` role
''''''''''''''''''''''''

- Correctly refresh the :man:`pam_mkhomedir(8)` configuration on changes by
  removing and installing the snippet again.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- In the :command:`autopostgresqlbackup` script, use the
  :command:`su  - postgres` command instead of the :command:`su postgres`
  command to start a login shell and switch to the correct home directory of
  the ``postgres`` user instead of staying in the :file:`/root/` home
  directory.  This avoids the issue during execution of the script via
  :command:`cron` where it would emit errors about not being able to change to
  the :file:`/root/` home directory due to the permissions.

:ref:`debops.prosody` role
''''''''''''''''''''''''''

- In the :ref:`debops.pki` hook script, use the correct configuration file name
  and check the Prosody configuration using the :command:`prosodyctl` command.

:ref:`debops.slapd` role
''''''''''''''''''''''''

- Move the Private Enterprise Number and LDAP namespace OIDs of the DebOps
  organization to a separate :file:`debops.schema` file to avoid duplicated
  OIDs in the ``cn=schema`` LDAP subtree.

  Existing installations might need to be recreated to avoid warnings about
  duplicate OIDs emitted during OpenLDAP operations.


`debops v1.2.2`_ - 2020-01-30
-----------------------------

.. _debops v1.2.2: https://github.com/debops/debops/compare/v1.2.1...v1.2.2

Added
~~~~~

General
'''''''

- The DebOps project directories can now include the
  :file:`ansible/global-vars.yml` file which can be used to define :ref:`global
  Ansible variables <global_vars>` that can affect playbook initialization.

:ref:`debops.docker_registry` role
''''''''''''''''''''''''''''''''''

- The :envvar:`docker_registry__basic_auth_except_get` variable allows to setup
  a simple authentication schema without the need to deploy a fully blown
  Docker Registry Token Authentication.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The firewall will accept the initial DHCPv6 solicit packets on the multicast
  port when IPv6 support is enabled.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- The GitLab backup :command:`cron` job can be enabled or disabled via
  a dedicated variable.

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

:ref:`debops.keyring` role
''''''''''''''''''''''''''

- The role will install the ``gpg`` APT package if it's missing from the host.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- The :command:`autopostgresqlbackup` script can be configured to tell the
  :command:`pg_dump` command to compress the generated backup files on the fly
  instead of creating a separate ``.sql`` file and compressing it afterwards.
  This mode is currently disabled by default.

:ref:`debops.python` role
'''''''''''''''''''''''''

- Expose Python 2.7 and Python 3.x versions via Ansible local facts.

:ref:`debops.rsyslog` role
''''''''''''''''''''''''''

- On Debian with the :command:`rsyslog` service in unprivileged mode, update
  permissions of the :file:`/var/log/` directory `reset`__ by the
  :command:`systemd` unit file on boot to allow writes by the ``syslog`` UNIX
  group.

  .. __: https://unix.stackexchange.com/questions/377376/

:ref:`debops.slapd` role
''''''''''''''''''''''''

- The :ref:`mailservice <slapd__ref_mailservice>` LDAP schema has been added to
  the :ref:`debops.slapd` role. It provides a set of object classes and
  attributes useful for defining e-mail recipients and simple mail distribution
  lists in the LDAP directory.

Changed
~~~~~~~

Mail Transport Agents
'''''''''''''''''''''

- The :envvar:`nullmailer__mailname` and the :envvar:`postfix__mailname`
  variables will use the host's FQDN address instead of the DNS domain as the
  mailname. This was done to not include the hostnames in the e-mail addresses,
  however this is better handled by Postfix domain nasquerading done on the
  mail relay host, which allows for exceptions, supports multiple DNS domains
  and does not break mail delivery in subtle ways. See the
  :ref:`debops.nullmailer` role documentation for an example configuration.

:ref:`debops.gunicorn` role
'''''''''''''''''''''''''''

- The role will use :command:`gunicorn3` binary by default if the Python 3.x
  runtime environment is available on the host.

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

:ref:`debops.nullmailer` role
'''''''''''''''''''''''''''''

- The upstream SMTP relay will be detected automatically using DNS SRV resource
  records, if they are defined.

:ref:`debops.postconf` role
'''''''''''''''''''''''''''

- If both :ref:`Devecot <debops.dovecot>` and :ref:`Cyrus <debops.saslauthd>`
  services are installed on a host, Postfix will be configured to prefer Cyrus
  for SASL authentication. This permits mail relay via the authenticated
  :ref:`nullmailer <debops.nullmailer>` Mail Transfer Agents with accounts in
  the LDAP directory. The preference can be changed using the
  :envvar:`postconf__sasl_auth_method` variable.

:ref:`debops.tinyproxy` role
''''''''''''''''''''''''''''

- Ensure that role creates service POSIX account and group, as well as uses the
  correct configuration file on older Ubuntu releases.

Fixed
~~~~~

:ref:`debops.gitlab_runner` role
''''''''''''''''''''''''''''''''

- Fix issue with GitLab Runner failing test jobs due to the default
  :file:`~/.bash_logout` script wiping the terminal on logout. The role will
  skip copying the :file:`/etc/skel/` contents on the new installations;
  existing script will be removed.

:ref:`debops.gunicorn` role
'''''''''''''''''''''''''''

- Fix version detection via Ansible local fact script in Python 3.x runtime
  environment.

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

:ref:`debops.yadm` role
'''''''''''''''''''''''

- Install :command:`yadm` from upstream on Ubuntu Xenial to provide newer
  version of the script than the one available in OS repositories.


`debops v1.2.1`_ - 2020-01-09
-----------------------------

.. _debops v1.2.1: https://github.com/debops/debops/compare/v1.2.0...v1.2.1

Added
~~~~~

:ref:`debops.ansible_plugins` role
''''''''''''''''''''''''''''''''''

- The ``parse_kv_config`` and ``parse_kv_items`` Ansible filter plugins now
  support the ``null`` value defined in the configuration entries. The values
  defined via additional variables can now be casted as strings, integers,
  floats or booleans to preserve their type.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Add `docker_server__install_virtualenv` setting to disable python virtualvenv installation.

:ref:`debops.gitlab` role
'''''''''''''''''''''''''

- Support for Gravatars is now configurable using role default variables.

:ref:`debops.postgresql_server` role
''''''''''''''''''''''''''''''''''''

- A given PostgreSQL server cluster can be configured to enable `standby
  replication mode`__, and receive streaming replication data from a master
  PostgreSQL server. See role documentation for examples.

  .. __: https://www.postgresql.org/docs/current/warm-standby.html

:ref:`debops.resolvconf` role
'''''''''''''''''''''''''''''

- The role can now define static DNS configuration to be merged with other DNS
  data sources in the :file:`/etc/resolv.conf` configuration file.

Changed
~~~~~~~

General
'''''''

- Reorder :file:`bootstrap.yml` Ansible playbook to also work for systems freshly
  installed from CD. :ref:`debops.apt` needs to be run early to regenerate
  :file:`/etc/apt/sources.list` which might still contain a now not functional
  CD entry.

- Quote octal values in various roles to prevent wrong interpretation by
  Ansible modules.

Fixed
~~~~~

Global
''''''

- The :file:`postldap.yml` playbook has been included in the global
  :file:`site.yml` playbook.

:ref:`debops.docker_server` role
''''''''''''''''''''''''''''''''

- Do not add empty entries from `docker_server__listen` to daemon.json.
  This causes the docker daemon to not parse the config and crash.

:ref:`debops.dovecot` role
''''''''''''''''''''''''''

- Ensure that the Postfix :file:`private/auth` socket is created by Dovecot.

:ref:`debops.ferm` role
'''''''''''''''''''''''

- The ``dmz`` firewall configuration will now not interpret the port as part of
  a IPv6 address anymore. We now protect the IPv6 address by surrounding it by
  ``[]``.


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
  ``item.location`` parameter is specified, overridding the default set of
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

- Readd :envvar:`users__default_shell` which was removed in `debops v1.0.0`_.

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

- The :ref:`debops.resolvconf` role has been added as a dpendency in the
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
  :envvar:`docker_server__storage_driver` variable.

:ref:`debops.etckeeper` role
''''''''''''''''''''''''''''

- The installation of :command:`etckeeper` will be disabled by default in
  Python 3.x-only environments. See :ref:`role documentation
  <etckeeper__ref_python3only>` for more details.

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
  configuration keys`__ between the old and new LXC version for comparsion.

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
  with assumtion that the domain is configured locally.

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

- Make sure logical volumes will only be shrinked when volume item defines
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
  existing UNIX accounts managed by the role; the mode can be overriden using
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
  in a YAML dictionary. The new :envvar:`gitlab__release` variable is used to
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
  Ansible. The :ref:`debops.debops` role now uses the new role to install
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
