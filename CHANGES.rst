Changelog
=========

.. include:: includes/all.rst

**debops-playbooks**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current playbook maintainer is drybjed_.


`debops-playbooks master`_ - unreleased
---------------------------------------

.. _debops-playbooks master: https://github.com/debops/debops-playbooks/compare/v0.2.9...master

Added
~~~~~

- Add support for custom Ansible environment variables in all playbooks.
  Environment can be configured using Ansible inventory variables. [drybjed_]

- Add debops.php_ role and its corresponding playbook. [drybjed_]

- Add debops.environment_ role with it's own playbook, and include it in the
  :file:`common.yml` playbook. [drybjed_]

- Add debops.authorized_keys_ role with its own playbook, and include it in
  the :file:`common.yml` playbook. This role replaces the ``debops.sshkeys`` role
  and is backwards-compatible with it. [drybjed_]

- Add debops.debops_api_ role and its corresponding playbook. [ypid_]

- Add debops.hashicorp_ role and its corresponding playbook. [drybjed_]

- Add Core Infrastructure Initiative (CII) Best Practices badge to the
  repository README. [ypid_]

- Add debops.nullmailer_ role and its playbook. [drybjed_]

- Add ``debops_service_bootstrap`` Ansible host group to allow to run
  debops.bootstrap_ against hosts not in the ``debops_all_hosts`` host
  group. [ypid_]

- Add debops.debops_fact_ role with corresponding playbook and include it in
  the :file:`common.yml` playbook. [drybjed_]

- Add debops.sysctl_ role with corresponding playbook and include it in
  the :file:`common.yml` playbook. [ypid_]

- Add debops.apt_listchanges_ and debops.apt_proxy_ roles with their
  corresponding playbooks. Both roles are included in the :file:`common.yml`
  playbook. [drybjed_]

- Add debops.apache_ role and its corresponding playbook. [ypid_]

- Add debops.gunicorn_ role and its corresponding playbook. [drybjed_]

- Add debops.netbox_ role and its corresponding playbook. [drybjed_]

- Add debops.cron_ role and its playbook, and include it in the
  :file:`common.yml` playbook. [drybjed_]

- Add debops.persistent_paths_ role and its corresponding playbook. [ypid_]

- Add alternative debops.dnsmasq_ playbook for use together with the
  debops.persistent_paths_ role. [ypid_]

- Add alternative debops.tinc_ playbook for use together with the
  debops.persistent_paths_ role. [ypid_]

- Add commonly used set of Jinja2 macros to the repository under
  `./templates/debops__tpl_macros.j2 <https://github.com/debops/debops-playbooks/blob/master/templates/debops__tpl_macros.j2>`_
  to have a central place where the file can be maintained and from where the
  latest version can be acquired. [ypid_]

- Add the debops.root_account_ role, included in the :file:`common.yml`
  playbook. This role contains functionality previously present in the
  debops.console_ role. This change will result in updated ``root`` account
  passwords, due to the changed location of the password files in the
  ``secret/`` directory. [drybjed_]

- Add ``flattened`` Jinja filter to debops__tpl_macros.js_. [ypid_]

- Add the ``debops.nfs_server`` Ansible role with a corresponding playbook.
  [drybjed_]

- Add the ``debops.nsswitch`` Ansible role with its corresponding playbook. The
  role is included in the :file:`common.yml` playbook. [drybjed_]

- Add the ``debops.avahi`` Ansible role with its corresponding playbook.
  [drybjed_]

- Add the ``debops.mosquitto`` Ansible role and its corresponding playbooks.
  [drybjed_]

- Add the ``debops.elastic_co`` Ansible role and its corresponding playbook.
  [drybjed_]

- Add the ``debops.kibana`` Ansible role and its corresponding playbook.
  [drybjed_]

- Add the ``debops.libvirtd_qemu`` role and playbook, update the
  ``debops.libvirtd`` playbook. [drybjed_]

- Add the ``debops.rabbitmq_server`` role and playbook. [drybjed_]

- Add the ``debops.rabbitmq_management`` role and playbook. [drybjed_]

- Add the ``debops.etc_aliases`` role and playbook. [drybjed_]

- Add the ``debops.unbound`` role and playbook. [drybjed_]

- Add the ``debops.ansible_plugins`` role. [drybjed_]

- Add Postfix-related roles: ``debops.saslauthd``, ``debops.opendkim``,
  ``debops.postscreen``, ``debops.postwhite``, ``debops.postconf``. [drybjed_]

- Add ``debops.cran`` Ansible role with the corresponding playbook. [drybjed_]

Changed
~~~~~~~

- Update debops.dokuwiki_ playbook. [drybjed_]

- Update debops.bootstrap_ playbook. [drybjed_]

- Update playbooks which use debops.php_ role to include the
  debops.apt_preferences_ role dependency. [drybjed_]

- Remove the debops.postfix_ role from the :file:`common.yml` playbook. The Postfix
  server is replaced by ``nullmailer`` on new installations.

  On existing installations, debops.nullmailer_ will detect Postfix and
  disable itself automatically. This means that the DebOps playbook won't
  manage the existing Postfix installations anymore using the :file:`common.yml`
  playbook. To enable Postfix management, add the host to
  ``[debops_service_postfix]`` inventory group. [drybjed_]

- Update the debops.owncloud_ playbook and add a playbook for debops.apache_
  support. [ypid_]

- Update debops.librenms_ playbook. [drybjed_]

- Update the ``ipaddr()`` filter plugin with the version from Ansible ``devel``
  branch. [drybjed_]

- Update the debops.lxc_ playbook to the new version. [ypid_]

- Update the debops.redis_ playbook to the new version. [drybjed_]

- Update the debops.dnsmasq_ playbook to the new version. [ypid_]

- Update the ``ldap_addr`` and ``ldap_entry`` Ansible modules to versions
  created by Jiri Tyr and proposed for inclusion in the Ansible modules
  library. These versions should work better with the latest Ansible 2.x
  releases. [drybjed_]

- Update debops.ifupdown_ playbook to support new features in the role. You will
  need to update your inventory, check the role documentation for more details.
  [drybjed_]

- Make sure that debops.tcpwrappers_ role is included in the debops.dnsmasq_
  playbook because the DNSmasq role notifies the debops.tcpwrappers_ handler in
  case of any changes. [drybjed_]

- Update the ``ldap_entry`` Ansible module to the new version. This is
  a non-backwards compatible change, roles that use ``ldap_entry`` will need to
  be updated to use the new module ``atributes`` parameter instead of
  specifying LDAP entry parameters directly as module parameters. [drybjed_]

- Update the debops.swapfile_ playbook to the new version. [ypid_]

- Treat the debops.core_ role like a normal service role by moving it to
  :file:`playbooks/service/core.yml`.
  This change is part of my effort to make DebOps usable on Qubes OS where you
  might only want to run a minimum set of roles.
  [ypid_]

- Update the debops.owncloud_ with Apache playbook to the new version. [ypid_]

- Update the debops.cryptsetup_ playbook to the new version. [ypid_]

- Update the debops.gitlab_ playbook to use role dependencies. [drybjed_]

- The order of the NFS server/client roles has been moved to be earlier in the
  main playbook to allow for mounting of the NFS shares early. [drybjed_]

- Update all playbooks that use the debops.java_ role with new
  debops.apt_preferences_ role dependency. [drybjed_]

- Update debops.salt_ playbook with new role dependencies. [drybjed_]

- Support dist upgrade from Debian Jessie to Debian Stretch using
  :file:`tools/dist-upgrade.yml`. [ypid_]

- Update the debops.elasticsearch_ playbook with new release of the role.
  [drybjed_]

- Update playbooks for new versions of debops.postfix_, debops.mailman_,
  debops.dovecot_ and debops.smstools_ roles. [drybjed_]

- Update the debops.etherpad_ playbook. [drybjed_]

- Update the ``profile_tasks.py`` callback to work correctly on Ansible 2.4.
  [drybjed_]

Deprecated
~~~~~~~~~~

- Support for Ansible 2.0 is deprecated due to the changes in ``ldap_attr`` and
  ``ldap_entry`` Ansible modules which require Ansible 2.1. Roles that don't
  use these Ansible modules should still work correctly on Ansible 2.0.
  [drybjed_]

Removed
~~~~~~~

- Remove the ``debops.sshkeys`` role, which is replaced by
  debops.authorized_keys_ role. [drybjed_]

- Remove the debops.ifupdown_ role form the :file:`common.yml` playbook and turn it
  into a regular service. The debops.ifupdown_ role is activated when hosts are
  placed in the ``[debops_service_ifupdown]`` Ansible host group. [drybjed_]

- Remove the ``debops.subnetwork`` role, its functionality has been merged with
  debops.ifupdown_ role. [drybjed_]

Fixed
~~~~~

- The ``ldap_attr`` and ``ldap_entry`` modules should now work correctly on
  Ansible 2.1. This is a non-backwards compatible change and it breaks
  compatibility with Ansible 2.0. [anzil]

- Fix compatibility of :file:`playbooks/tools/dist-upgrade.yml` and
  ``apt_preferences__debian_stable_default_preset_list``.
  Previously,
  :file:`/etc/apt/preferences.d/debops_apt_preferences_all_Debian.pref` might
  not have been removed resulting in packages from backports getting installed
  during the upgrade. [ypid_]

Security
~~~~~~~~

- Terminate playbook execution as soon as possible if a vulnerable Ansible version is used.
  The minimum Ansible version without known vulnerabilities is Ansible 2.1.4.
  The check is run as part of the :file:`common.yml` playbook file in a
  separate playbook which has ``gather_facts`` explicitly turned of and the
  task being delegated to the Ansible controller to avoid possible connection
  attempts to remote hosts before the check had the opportunity to terminate
  a vulnerable Ansible instance.
  This playbook is run with no limitation on remote hosts meaning it will also
  run the check even if the current Ansible run is limited to a host which is
  not even managed by DebOps.
  This check became necessary because some distributions only provide Ansible
  versions with known vulnerabilities and some users are unaware.
  Note that you will need at least v2.1.5 or v2.2.2 because only they fix all
  currently known vulnerabilities as well as some bugs (e.g. `#20253`_) for
  advanced templating features used by some DebOps roles such as debops.ferm_.
  Refer to `Ansible Security`_ for details.
  [ypid_]

.. _#20253: https://github.com/ansible/ansible/issues/20253

`debops-playbooks v0.2.9`_ - 2016-07-07
---------------------------------------

.. _debops-playbooks v0.2.9: https://github.com/debops/debops-playbooks/compare/v0.2.8...v0.2.9

Added
~~~~~

- Add debops.snmpd_ role dependencies to :file:`service/snmpd.yml` playbook.
  [drybjed_]

- Add debops.unattended_upgrades_ role to the :file:`common.yml` playbook as
  well as its own :file:`service/unattended_upgrades.yml` playbook. The support for
  ``unattended-upgrades`` package in debops.apt_ role will be removed.
  [drybjed_]

- Add debops.apt_cacher_ng_ role to it's own
  :file:`service/apt_cacher_ng.yml` playbook. The server-side support for the
  :program:`apt-cacher-ng` package in debops.apt_ role has be removed. Client-side
  support is being reworked in debops.apt_. [ypid_]

- Add debops.gitlab_runner_ role and playbook. [drybjed_]

- Add debops.logrotate_ role and playbook, available as a standalone service
  as well as included in the :file:`common.yml` playbook. [drybjed_]

- Add the debops.apt_install_ role with its own playbook as well as in the
  :file:`common.yml` playbook. [drybjed_]

- Add the "role dependency" debops.apt_preferences_ to :file:`service/apt.yml`.
  Especially with Debian Stretch enabled in :manpage:`sources.list(5)`, not
  running debops.apt_preferences_ together with debops.apt_ could risk
  installing new packages from Stretch. Using ``apt_preferences__preset_list``
  can avoid that. [ypid_]

- Ensure that the :file:`galaxy/requirements*` files are up-to-date by making
  it easy to regenerate them and check if they are up-to-date via Travis CI.
  [ypid_]

- Add debops.preseed_ role dependencies to :file:`service/preseed.yml` playbook.
  [ypid_]

- Add back some of the roles that were removed previously from Ansible Galaxy
  requirements. They are still present in the playbook, and will be removed at
  a later date. [drybjed_]

- Add debops.resources_ role and its playbook. [drybjed_]

Changed
~~~~~~~

- Update the :file:`service/iscsi.yml` playbook to use roles that were previously
  hard dependencies of the debops.iscsi_ role. [drybjed_]

- Update the variables related to debops.sshd_ due to change in the variable
  naming scheme. You might need to update your Ansible inventory. [drybjed_]

- Update the :file:`service/tinc.yml` playbook with support for new debops.tinc_
  release. [drybjed_]

- Update the :file:`service/mailman.yml` playbook with support for new
  debops.mailman_ release. [drybjed_]

- Moved roles dependencies from ``debops.subnetwork`` to subnetwork playbook. [ypid_]

- Update debops.apt_cacher_ng_ playbook and add support for :program:`nginx` proxy
  for the cache. [drybjed_]

- Replace ``app/gitlab_ci*.yml`` playbooks with debops.gitlab_runner_
  playbook. The old GitLab CI and GitLab CI Runner roles will no longer be
  active by default, since GitLab CI has been merged into GitLab itself.
  [drybjed_]

- Update the debops.rsyslog_ playbook as well as the :file:`common.yml` playbook
  to support the rewritten debops.rsyslog_ role. [drybjed_]

- Update the debops.ntp_ playbook and :file:`common.yml` playbook to use the new
  variable names. [drybjed_]

- Update debops.mariadb_server_ playbook to include its role dependencies.
  [drybjed_]

- Update the :file:`service/postgresql_server.yml` playbook to use new namespaced
  variables. [drybjed_]

- Update the :file:`service/postgresql.yml` playbook to use new namespaced
  variables. [drybjed_]

- Run debops.apt_ earlier in the :file:`common.yml` playbook to setup things
  like APT proxy and :manpage:`sources.list(5)` for other roles. [ypid_]

- Update :file:`service/ruby.yml` playbook to use new role variables. [drybjed_]

- Update :file:`service/goland.yml` playbook to use new role variables. [drybjed_]

- Update Changelog and other documentation to current project standards.
  [drybjed_]

Removed
~~~~~~~

- Remove debops.directories_ role and replace it with debops.resources_,
  which is included in the :file:`common.yml` playbook. [drybjed_]

Fixed
~~~~~

- Fix compatibility issues of custom lookup plugins in Ansible v2.1+. [abadger]


`debops-playbooks v0.2.8`_ - 2016-02-07
---------------------------------------

.. _debops-playbooks v0.2.8: https://github.com/debops/debops-playbooks/compare/v0.2.7...v0.2.8

Added
~~~~~

- Add debops.swapfile_ role. [drybjed_]

- Add debops.atd_ role, included in the :file:`common.yml` playbook by default.

  The ``at`` and ``batch`` commands can be used to schedule delayed jobs using
  Ansible ``at`` module. [drybjed_]

- Add debops.dhparam_ role, included in the :file:`common.yml` playbook by
  default. [drybjed_]

- Add debops.sshd_ configuration variables to debops.apt_preferences_,
  debops.ferm_ and debops.tcpwrappers_ configuration in common playbook.
  [drybjed_]

- Add set of common "service" playbooks that invoke Ansible roles that are used
  on all hosts. [drybjed_]

- Add playbook for debops.ntp_ role and update :file:`common.yml` playbook with
  debops.ntp_ firewall configuration. [drybjed_]

- Add ``[debops_service_*]`` host groups to all relevant playbooks and clean up
  the ``hosts`` line in all playbooks to use YAML lists instead of Ansible
  patterns. This should ensure that during transition from colons to commas
  there shouldn't be any issues. [drybjed_]

  You can use :command:`sed --regexp-extended --in-place '/\[debops_service_/! s/^\[debops_(.+)\]$/[debops_service_\1]/' hosts`
  to update your inventory file. [ypid_]

- Add debops.cryptsetup_ role, which can be used to manage filesystems
  encrypted using LUKS. Role was created by Robin Schneider. Thanks! [drybjed_]

- Add debops.apt_preferences_ role to :file:`service/postgresql.yml` playbook.
  [drybjed_]

- Add missing :program:`ferm` configuration for debops.postfix_ role. [drybjed_]

- Add missing playbooks for roles included in :file:`common.yml` playbook so that
  they can be easily executed on their own. [drybjed_]

Changed
~~~~~~~

- All playbooks now use ``become: True`` instead of ``sudo: True`` to enable
  privileged operation. [drybjed_]

- Redesign common playbooks to only work with hosts that are in
  ``[debops_all_hosts]`` inventory group. This should improve support for
  non-DebOps managed hosts in Ansible inventory, but it requires modification
  of existing inventories. [drybjed_]

- Update the Postfix, nginx and slapd playbooks to include the firewall and TCP
  Wrappers roles. OpenLDAP and nginx Ansible host groups have been renamed, you
  will need to update the inventory. Postfix playbook is prepared to manage
  Postfix as standalone service, not part of the :file:`common.yml` playbook.
  [drybjed_]

- Move all role playbooks to :file:`service/` subdirectory and create symlinks in
  old locations. [drybjed_]

- Update :file:`service/docker.yml` playbook and include additional roles required
  to configure the service properly. [drybjed_]

- Update "Getting Started Guide" and parts of other documentation. [drybjed_]

- Moved roles dependencies from debops.owncloud_ to owncloud playbook. [ypid_]

- Moved roles dependencies from debops.tinc_ to tinc playbook. [le9i0nx_]

- Moved roles dependencies from debops.postgresql_server_ to
  postgresql_server playbook. [drybjed_]

- Update the :file:`common.yml` playbook and :file:`service/pki.yml` playbook with new
  debops.pki_ role requirements. [drybjed_]

- Allow execution of debops.pki_ role with ``role::pki:secret`` tag so that
  it will create secret directories but nothing else. [drybjed_]

Removed
~~~~~~~

- Remove the ``default([])`` alternatives from playbooks to make them work
  correctly on Ansible v1. [drybjed_]

- Remove legacy tags from role playbooks. [drybjed_]

- Remove ``d([])`` from :file:`common.yml` playbook to pass the variables correctly
  between roles. [drybjed_]

Fixed
~~~~~

- Fix support for ``no_log: True`` parameter in ``ldap_entry`` Ansible module,
  so that it works correctly on Ansible v2. [drybjed_]


`debops-playbooks v0.2.7`_ - 2015-10-15
---------------------------------------

.. _debops-playbooks v0.2.7: https://github.com/debops/debops-playbooks/compare/v0.2.6...v0.2.7

Added
~~~~~

- Add debops.lvm_ role. [drybjed_]

- Add debops.iscsi_ role. [drybjed_]

- Add debops.libvirt_ and debops.libvirtd_ roles. debops.kvm_ role is
  dropped, due to being replaced by debops.libvirtd_. Hosts in
  ``[debops_kvm]`` host group will need to be moved to ``[debops_libvirtd]``,
  there might be some variable changes as well. [drybjed_]

- Add a context-based tags to common playbook as an experiment (``libvirt(d)``
  roles already use them). Context tags are inspired by ``debtags`` and will
  allow more fine-grained control over playbook tasks, when roles start to use
  them internally. Old-style tags will be phased out after some time.
  [drybjed_]

- Add debops.librenms_ role. [drybjed_]

- Add debops.core_ role as well as :file:`core.yml` playbook and replace the
  :file:`root.yml` playbook. This change may affect any ``root_*`` variables set in
  the inventory. Check debops.core_ role documentation for new variable
  names. [drybjed_]

- Add debops.fcgiwrap_ role. [drybjed_]

- Add new role tags in all playbooks. [drybjed_]

- Add debops.grub_ role, created by Patryk Ściborek (scibi_). Thanks!
  [drybjed_]

- Add debops.docker_ role. [drybjed_]

- Add ``globmatch()`` Ansible filter plugin. Using this filter, you can match
  strings or lists of strings against a shell glob pattern (a string or a list
  of patterns). This can be used to easily match one or more strings in a list
  using ``*`` and ``?`` characters. [drybjed_]

- Add debops.docker_gen_ role. [drybjed_]

- Add ``ldappassword`` filter. [scibi_]

- Add debops.postgresql_server_ role. [drybjed_]

Changed
~~~~~~~

- Hosts in ``[debops_no_common]`` host group will no longer run a common
  playbook. [drybjed_]

- Lookup plugins ``task_src``, ``template_src`` and ``file_src`` are updated
  using input from James Cammarata to work both in old Ansible 1.x series as
  well as in the new 2.x series. Thanks! [drybjed_]

- Split the :file:`environments.yml` playbook into smaller plays included in the
  main playbook to see if this model has any issues. This change should make
  user of specific role plays easier on the command line and from other
  playbooks. [drybjed_]

- Split :file:`virtualization.yml` playbook into separate plays. [drybjed_]

- All playbooks have been split into small plays. Playbook directories have
  shorter names, which are easier to use from the command line. [drybjed_]

Removed
~~~~~~~

- Remove :file:`root.yml` playbook and its additional files - its functionality has
  been moved to debops.core_ Ansible role. [drybjed_]


`debops-playbooks v0.2.6`_ - 2015-07-14
---------------------------------------

.. _debops-playbooks v0.2.6: https://github.com/debops/debops-playbooks/compare/v0.2.5...v0.2.6

Added
~~~~~

- Add debops.fail2ban_ role. [drybjed_]

- Add debops.preseed_ role. [drybjed_]

- Add debops.ipxe_ role. [drybjed_]

- Add debops.tftpd_ role. [drybjed_]

- Add debops.tgt_ role. [drybjed_]

- Add variables to set admin home directory group and permissions in
  :file:`bootstrap.yml` playbook. [drybjed_]

- Add debops.rstudio_server_ role. [drybjed_]

- Add debops.tinc_ role. [drybjed_]

- Add ``ansible_local.timezone`` fact which returns currently set timezone in
  :file:`/etc/timezone`. Fact provided by Ansible itself in
  ``ansible_date_time.tz`` is not suitable to use in application configuration
  files. [drybjed_]

- Add debops.snmpd_ role. [drybjed_]

- Add debops.memcached_ role. [drybjed_]

- Add MariaDB server and client roles. [drybjed_]

Changed
~~~~~~~

- Ansible will now try and read the remote host UUID using ``dmidecode`` and
  prefer that over using a randomly generated UUID if possible. This works on
  hardware hosts and virtual machines, but shouldn't in containers. [drybjed_]

- During :file:`root.yml` playbook, grab only the last line of ``dmidecode`` output
  in case that it decides to emit comments about not supporting older releases
  in ``STDOUT``. [drybjed_]

- Update of the :file:`bootstrap.yml` playbook; there are now more variables that
  define the administrator account, admin account will be now a "system"
  account by default (UID < 1000). Playbook checks if an account with a given
  name already exists and does not change its parameters if it does. Admin
  account will be in more groups by default (``admins`` (passwordless sudo
  access), ``staff`` and ``adm``). [drybjed_]

- Move the Changelog references to the end of the file and remove duplicates,
  so that Sphinx does not complain about them. [drybjed_]

- Replace old headers in Changelog to use current header order. [drybjed_]

- Move relevant documentation to ``debops-playbooks`` repository. [drybjed_]

Removed
~~~~~~~

- Remove debops.ansible_ role from requirements, you should switch to
  creating an :command:`ansible` Debian package and installing it on remote servers
  using local APT repository. [drybjed_]

- Remove debops.encfs_ role from requirements, it's not used anymore and is
  ill designed to be used on servers at this point. [drybjed_]

- Remove debops.safekeep_ role from requirements, SafeKeep is not in
  official Debian repositories therefore installation requires manual steps,
  debops.rsnapshot_ is a better alternative. [drybjed_]

- Remove debops.debug_ role from requirements, :file:`tools/debug.yml` playbook
  should be a better alternative and it's easier to use. [drybjed_]

- Convert :file:`bootstrap.yml` playbook to an Ansible role. [drybjed_]


`debops-playbooks v0.2.5`_ - 2015-04-01
---------------------------------------

.. _debops-playbooks v0.2.5: https://github.com/debops/debops-playbooks/compare/v0.2.4...v0.2.5

Added
~~~~~

- Add debops.dokuwiki_ role. [drybjed_]

- Add a "testing channel" Galaxy requirements file, to be used to download
  Ansible roles with "testing" branch instead of "master". [drybjed_]

- Reto Gantenbein created a `Dovecot`_ role which has been added to the DebOps
  project. Thanks! debops.dovecot_ can be used to manage IMAP/POP3 service
  which will let you access your mail remotely over a secure connection.
  [ganto_, drybjed_]


`debops-playbooks v0.2.4`_ - 2015-03-26
---------------------------------------

.. _debops-playbooks v0.2.4: https://github.com/debops/debops-playbooks/compare/v0.2.3...v0.2.4

Added
~~~~~

- Add separate "root fact" directory where applications are installed, by
  default the same as the path for service home directories. [drybjed_]

- Install ``python-pip`` during bootstrapping. [htgoebel_]

- Add a way to install custom packages during bootstrapping. [drybjed_]

- Add debops.stunnel_ role. [drybjed_]

Changed
~~~~~~~

- Reorder :file:`networking.yml` playbook to run network-related roles before main
  services and applications. This should make sure that networking is correctly
  set up when it's needed. [drybjed_]


`debops-playbooks v0.2.3`_ - 2015-03-05
---------------------------------------

.. _debops-playbooks v0.2.3: https://github.com/debops/debops-playbooks/compare/v0.2.2...v0.2.3

Added
~~~~~

- Added new lookup plugins, ``file_src`` and ``template_src`` which allow
  custom template and file search paths in roles. [rchady]

- You can set global "root flags" on hosts using :file:`root.yml` playbook.
  Ansible roles can check for their presence or absence and automatically
  change their behavior. [drybjed_]

Changed
~~~~~~~

- Roles in :file:`common.yml` playbook are rearranged to better support LDAP
  integration and avoid possible SSH lockdown if host was not prepared using
  :file:`bootstrap.yml` playbook or preseeding. [drybjed_]

- Scripts which provide custom facts will be installed on the first run of
  the :file:`root.yml` playbook. First such script provides a list of currently
  enabled Linux capabilities, in ``ansible_local.cap12s`` fact tree.
  [htgoebel_, drybjed_]

- :file:`bootstrap.yml` playbook will check if it can change the hostname before
  doing it using Linux capabilities. [htgoebel_, drybjed_]


`debops-playbooks v0.2.2`_ - 2015-02-25
---------------------------------------

.. _debops-playbooks v0.2.2: https://github.com/debops/debops-playbooks/compare/v0.2.1...v0.2.2

Added
~~~~~

- Add support for STARTTLS in ``ldap_attr`` and ``ldap_entry`` modules [psagers]

Changed
~~~~~~~

- Fix issue with ``ldap_entry`` not handling ``no_log: True`` in argument list
  properly [drybjed_]


`debops-playbooks v0.2.1`_ - 2015-02-24
---------------------------------------

.. _debops-playbooks v0.2.1: https://github.com/debops/debops-playbooks/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Move :file:`library/` directory into correct place and sort modules in
  subdirectories mirroring the official layout. [drybjed_]

`debops-playbooks v0.2.0`_ - 2015-02-22
---------------------------------------

.. _debops-playbooks v0.2.0: https://github.com/debops/debops-playbooks/compare/v0.1.0...v0.2.0

Added
~~~~~

- New role: debops.rsnapshot_ [drybjed_]

Changed
~~~~~~~

- Variables from :file:`bootstrap.yml` playbook can now be customized using
  inventory. [drybjed_]

- Bootstrap variable names have been changed to be similar to what is used in
  other DebOps roles. Variable that specifies SSH key to install is now
  a normal Ansible list. [drybjed_]


debops-playbooks v0.1.0 - 2015-02-16
------------------------------------

Added
~~~~~

- New paths have been added to :file:`root.yml` service paths. [drybjed_]

Changed
~~~~~~~

- Format of the Changelog is modified to reflect new versioning. Old entries are
  preserved. [drybjed_]

- ``ansible_local.root.home`` default path has been changed from :file:`/var/lib`
  to :file:`/var/local` to move home directories out of the way of the system
  packages. [drybjed_]

- :file:`root.yml` service paths that are already configured on remote host as facts will
  override playbook or inventory changes to protect already installed services
  from future changes. [drybjed_]

****

2015-02-12
----------

Playbook updates
~~~~~~~~~~~~~~~~

Due to practical reasons, role updates will be written in roles themselves from
now on, in :file:`CHANGES.rst` files.

New "root variable" has been added to :file:`root.yml` playbook,
``ansible_local.root.uuid``. It will contain a random UUID generated on first
DebOps run. It can be used to uniquely identify an instance of a particular
host.


2015-02-06
----------

Role updates
~~~~~~~~~~~~

OpenLDAP server managed by debops.slapd_ role has gained support for TLS out
of the box, using certificates managed by debops.pki_ role. By default,
``slapd`` server listens for normal plain text connections, which can be
protected by the client requesting a StartTLS session, as well as for encrypted
SSL/TLS connections. This also marks the removal of Beta status from
debops.slapd_ role.

To stay on the safe side, debops.auth_ role, which configures
:file:`/etc/ldap/ldap.conf`, will automatically set encrypted connections to
OpenLDAP server using ``ldaps://`` protocol. You can of course change that
using role default variables.

Playbook updates
~~~~~~~~~~~~~~~~

To make LDAP use easier within Ansible playbooks, I've included two
`Ansible LDAP modules`_ created by Peter Sagerson in the main DebOps playbook
:file:`library/` directory, which makes them available anywhere within DebOps
project directories (in playbooks and roles). You can use ``ldap_entry`` and
``ldap_attr`` modules to manipulate your LDAP database, look in each module
source code for examples.


2015-02-05
----------

Role updates
~~~~~~~~~~~~

debops.mysql_ role can now configure a MySQL server with SSL support enabled
by default, using PKI infrastructure managed by debops.pki_ role.

debops.nginx_ role gained support for setting server-wide (as in, per domain)
``allow/deny`` rules, which is more secure than just per-location (which was
available previously). You can use Ansible lists to specify which hosts or
networks have access to the server.

You can now configure HTTP Basic Authentication in debops.nginx_ role. It
works on a server level (restricted access to individual servers), as well as
on the host level (restricted access to all nginx servers configured on this
host). debops.nginx_ has a built-in support for ``htpasswd`` files - you
specify a list of user accounts to configure in Ansible inventory, and
passwords themselves are stored in :file:`secret/` directory, managed by
debops.secret_ role.


2015-02-04
----------

Role updates
~~~~~~~~~~~~

I have found out that some applications do not support SSL/TLS certificate
chains correctly. Because of that, I have added a separate PKI realm,
:file:`/etc/pki/service/`, with corresponding Root Certificate Authority, which
will sign certificates directly. It is meant for internal use only, each host
in a cluster has its own certificate shared by all services on this host,
private key is accessible for users belonging to ``ssl-cert`` system group.

For reference, `Debian Bug #630625`_ which indicates that MySQL does not
support certificate chains out of the box. If other such services are found,
they will now use ``service`` PKI realm by default.

2015-02-03
^^^^^^^^^^

Role updates
************

debops.nginx_ role will now track HTTP and HTTPS ``default_server``
configuration option separately, which should make it even more roboust and
hard to break accidentally. Code which selected ``default_server`` was moved
out of the server template and into separate Ansible tasks.

Nginx role has exposed two variables using local Ansible facts:

- ``ansible_local.nginx.user`` is the default system user (``www-data``) which
  is used to run the webserver. Some of the roles need to give read-only or
  read-write access to his user for specific files. To have it work properly,
  debops.nginx_ role needs to be run before your own role, or you need to
  have it in your role's dependencies.

- ``ansible_local.nginx.www`` is the default directory for web-accessible files
  (:file:`/srv/www`). Most of the time you will use it by creating separate
  subdirectory for a specific system user. Nginx role uses a specific structure
  based on this path to automatically generate ``root`` configuration
  parameters;


Playbook updates
****************

New playbook, :file:`tools/dist-upgrade.yml` has been added. It should help with
upgrading to next version of your favorite OS, currently supported upgrade
paths are from Debian Wheezy to Debian Jessie and from Ubuntu Trusty to Ubuntu
Utopic.

To use the new playbook on a selected host, run command::

    debops tools/dist-upgrade --limit hostname

Playbook is idempotent and it shouldn't perform an upgrade on already upgraded
hosts. After an upgrade is performed you should receive email message with the
log of the procedure for review. After that you might want to re-run at least
DebOps common playbook to make sure that any changes are accounted for and
reboot the host.

Just a reminder, that at this time Debian Jessie is still a Testing
distribution and you shouldn't run the upgrade playbook on your production
systems, unless you know what you are doing. DebOps playbooks and roles should
work correctly installed on either Wheezy or Jessie (if not, post an issue),
but they are not tested against an upgrade from one distribution to another.

I've created a `separate dist-upgrade label`_ for issues related to upgrade
procedure. You should check it out before upgrading. If you find any issues
regarding DebOps roles after performing an upgrade, please post them in
`DebOps Playbooks`_ repository so that they can be tracked in one place.


2015-02-01
----------

Role updates
~~~~~~~~~~~~

Small updates in debops.pki_ role:

- previously Diffie-Hellman parameter regeneration meant that on each Ansible
  run contents of :file:`/etc/pki/` directory would change. Because role creates
  a snapshot of :file:`/etc/pki/` directory on any changes and sends it to Ansible
  Controller, if you keep your inventory and secrets in a :command:`git` repository,
  it meant that your repository would constantly grow. Now debops.pki_ role
  will archive DH parameter files only the first time the snapshot file is
  created; subsequent snapshots will ignore them, and thus no changes will be
  recorded and snapshot file will not need to be archived, unless something
  else changes, for example certificates are added or updated.

- you can now disable or change the frequency of Diffie-Hellman parameter
  regeneration using inventory variables. Default frequency has been changed
  from ``daily`` to ``weekly``.


2015-01-31
----------

Playbook updates
~~~~~~~~~~~~~~~~

New playbook, :file:`root.yml` has been added and part of the :file:`common.yml`
playbook has been moved there. This playbook is meant to prepare the system for
the rest of the DebOps roles by creating a set of base directories:

- a root directory for service home directories, by default :file:`/var/lib`
- a root directory for local data managed by the host, :file:`/srv`
- a root directory for backups, both automated and manual, :file:`/var/backups`

Paths to these directories are saved in Ansible local facts. Other DebOps roles
can then access them using ``ansible_local.root`` hierarchy, for example::

    role_home:   '{{ ansible_local.root.home   + "/role" }}'
    role_data:   '{{ ansible_local.root.data   + "/role" }}'
    role_backup: '{{ ansible_local.root.backup + "/role" }}'

Because of the way that Ansible manages dict variables,
``ansible_local.root.*`` local facts will be required on all hosts managed by
DebOps playbooks and roles - otherwise you need to specifically check for
existence of ``ansible_local`` and ``ansible_local.root`` variables before
using them to avoid errors about missing variables.

If you use DebOps playbooks, this should be handled for you automatically. If
you use DebOps roles separately, you can add an include of :file:`root.yml`
playbook to your set of playbooks and these facts should be created for you
automatically. :file:`root.yml` does not need to be included in all your playbooks,
just in the first one at the beginning.

At the moment those variables are not used in any DebOps roles, that will
change over time after a period of testing.


2015-01-28
----------

Role updates
~~~~~~~~~~~~

debops.reprepro_ role is no longer a dependency of debops.apt_. Instead
it's configured like any other service, by adding a host to
``[debops_reprepro]`` host group. This allows you to create separate hosts with
different repositories if needed.

Default configuration of debops.reprepro_ role has 3 repositories:

- a backport repository configured for your installed release (for example on
  Debian Wheezy it will manage packages for ``wheezy-backports``). You can
  upload to this repository directly;

- a "staging" repository for your organization, ``<release>-<domain>-staging``.
  You can upload to this repository directly;

- a "production" repository for your organization, ``<release>-<domain>-prod``,
  this repository is currently managed manually from the ``reprepro`` user
  account. You can promote packages to it from ``-staging`` repository using
  ``reprepro pull`` command;

You can also enable mirrors of selected distributions as needed, which allows
you to use local APT mirror as a buffer between official repositories and your
servers, if you need it. To upload packages to repositories you can use
``dput`` command to upload ``*.changes`` files over HTTPS.

debops.reprepro_ role automatically manages its GnuPG repository keys and
makes snapshots of current keyring state which are then uploaded to Ansible
Controller's :file:`secret/` directory. In case of a reinstall, role will reuse
already existing GnuPG keys if they are found on Ansible Controller.

There are many more configuration options prepared in debops.reprepro_,
I suggest that you read its :file:`defaults/main.yml` file to see what's available.

Because of above changes, you need to separately add your local repositories in
debops.apt_ configuration variables. To make it easier, there is now
a separate list variable for APT key definitions (``apt_keys``, as well as
a way to add APT keys and repositories in a "delayed" way - instead of
configuring your own repository immediately on first install, which could
result in an error if repository is not yet set up, you can add configuration
in separate set of ``apt_{keys,sources}_delayed`` variables which will be used
only after debops.apt_ role had configured a host once.

Another small change in debops.apt_ is modification of conditional package
installations - instead of separate :command:`apt` module calls, packages are enabled
dynamically during Ansible run using ``set_fact`` module. debops.apt_ will
now also correctly distinguish Debian and Ubuntu firmware packages which are
named differently between those two distributions.


2015-01-21
----------

Role updates
~~~~~~~~~~~~

Webserver status page has been enabled by default in debops.nginx_, it's
accessible on :file:`/nginx_status` location, initially only from localhost
addresses (from the webserver itself). You can add additional IP addresses or
CIDR ranges using separate list, ``nginx_status``.

Fix for `CVE-2013-4547`_ has been removed from the server template, since the
issue has already been mitigated in Debian.


2015-01-20
----------

Role updates
~~~~~~~~~~~~

debops.gitlab_ci_ role has been updated to support `GitLab CI`_ 5.4, with
GitLab 7.7 providing authorization based on OAuth. Due to the changes in GitLab
CI itself, some configuration variables have been changed - check the role
defaults for new ones (mainly, you can define only 1 GitLab instance to connect
to).

debops.users_ role has been slightly cleaned up and ``root``-proofed - it
shouldn't make an error if you are connecting to your hosts directly as
``root`` account anymore. Role uses ``default(omit)`` filter in its tasks,
which means that DebOps now requires Ansible >= 1.8 for correct operation.

New playbook plugins
~~~~~~~~~~~~~~~~~~~~

`Hartmut Goebel`_ created a small lookup plugin, ``with_lists``, which allows
you to use lists of items as "items" themselves, see an example in the
`with_lists plugin`_. Thanks!


2015-01-18
----------

Role updates
~~~~~~~~~~~~

debops.gitlab_ role has been finally rewritten. Lots of important changes:

- support for `GitLab`_ 7.7 out of the box, even before official release ;)

- new home directory, :file:`/var/local/git/`, you might want to reinstall your
  GitLab instance from scratch or take care with moving your old instance files
  to new location;

- role does not depend on configuration file hashes anymore, updates should be
  much easier to perform and support for new versions should be included in
  a more timely manner;

- debops.gitlab_ will configure a daily backup of the application data to
  :file:`/var/backups/gitlab/`, backup files older than a week should be
  automatically cleaned up;

- new GitLab install uses a random password stored in the DebOps :file:`secret/`
  directory instead of the official password. Default admin account will have
  an email address in your domain instead of ``admin@example.com``, so random
  bounced mails shouldn't be a problem anymore;

Playbook updates
~~~~~~~~~~~~~~~~

:file:`bootstrap.yml` playbook gained new tasks which can be used to set hostname
and domain on a given host. You can define ``bootstrap_hostname`` or
``bootstrap_domain`` variables in inventory and Ansible will try to enforce
these settings on a given host as well as in :file:`/etc/hosts`. This functionality
makes the :file:`tools/fqdn.yml` playbook redundant, so it's removed.

2015-01-13
----------

Happy New Year 2015!

PKI rewrite
~~~~~~~~~~~

I've worked on debops.pki_ role since December, holiday season delayed it
slightly, but finally it is here. :-)

New PKI infrastructure in DebOps is designed around creating and managing
Certificate Authorities on the Ansible Controller, inside :file:`secret/` directory
managed by debops.secret_, signing Certificate Requests generated by remote
hosts and sending back certificates. There's 1 Root CA certificate you need to
import into your browser or host certificate store and after that, all other
servers should show up in your browser as accepted automatically.

You can also very easily copy your own certificates signed by an external CA,
with private keys if needed, to your servers using a set of directories in the
:file:`secret/` directory.

Several roles which depended on the old debops.pki_ role have been now
updated as well and take advantage of functionality present in the new PKI
infrastructure. These roles are:

- debops.nginx_
- debops.postfix_
- debops.postgresql_
- debops.boxbackup_

If you use any of these roles in your infrastructure, take care to make sure
that your certificates are moved into new directory structure and configuration
is updated as needed.

If there are any questions regarding new PKI and how to use it, feel free to
ask them on the IRC channel or on the mailing list.


2014-12-23
----------

Role updates
~~~~~~~~~~~~

debops.users_ role can now set or update user passwords (by default no
passwords are set).

debops.ntp_ role has gained support for :program:`ntpd` daemon, thanks to
`RedRampage`_. Because of the issues with role dependency variables and Jinja,
access to NTP service through firewall is now controlled by a separate
variable, ``ntp_firewall_access``. By default, remote access is disabled.


2014-12-05
----------

New roles
~~~~~~~~~

- debops.salt_ role allows you to install and configure `Salt`_ Master
  service. You can use this to create Salt control host to which other hosts
  (Salt Minions) can connect to. At the moment configuration is very basic,
  Salt master will automatically listen to IPv6 connections and firewall will
  be configured to accept connections on default ports.

Role updates
~~~~~~~~~~~~

Salt Minion preseeding has been added in debops.apt_ (current Debian Preseed
configuration is there, will be moved in the future to separate role),
debops.lxc_ and debops.openvz_ roles. Automatic minion installation is
disabled by default and can be enabled separately for each "mode" - Debian
Preseed postinst script in case of physical hosts or KVM virtual machines, LXC
template script for LXC containers, OpenVZ bootstrap script for OpenVZ
containers. After installation, ``salt-minion`` will try to connect to ``salt``
host, so make sure that it's present in your DNS configuration for best
results.

2014-12-03
----------

Role updates
~~~~~~~~~~~~

Continuing the `GitLab`_ revamp, debops.gitlab_ci_runner_ role has also been
refactored and is unfortunately not compatible with the previous version,
reinstall of the nost is recommended.

Runner home directory has been moved to :file:`/var/local/` directory, most of role
dependencies have been dropped and role now needs less upkeep than before. You
can read about changes in `latest commit`_.

2014-12-02
----------

`DebOps mailing list`_ has been moved to groups.io_.

Role updates
~~~~~~~~~~~~

debops.gitlab_ci_ role has been significantly refactored. Due to bug in
GitLab CI 5.0 at the moment this version cannot be installed, so I decided to
use this opportunity to make some deep changes in the role. GitLab CI home has
been moved to :file:`/var/local/gitlab-ci/` directory, and various tasks related to
updating the application have been streamlined. You can read more information
about various changes in the `commit message`_.

2014-12-01
----------

`Hartmut Goebel`_ has joined DebOps team and wrote an excellent guide for using
DebOps scripts and playbooks with Vagrant on single and multiple hosts. It's
available in `DebOps Examples`_ repository.

Role updates
~~~~~~~~~~~~

All DebOps roles again use Ansible `devel` branch on Travis CI for tests.

debops.debops_ role has been rewritten and updated to support current project
installation method. By default only DebOps scripts will be installed system
wide, but you can also install playbooks and roles to `/usr/local` by setting
a variable. Dependency on debops.ansible_ role has been dropped and that role
will be removed in the future. You can install Ansible from a Debian repository
or by providing your own ``.deb`` package.

`RedRampage`_ has provided a failover code for debops.dhcpd_ role which
should help set up failover DHCP servers. Thanks!

Several DebOps roles had a small fixes related to ``ansible-playbook --check``
command, which can now be used to check for possible changes before applying
them on the remote hosts. Due to bugs in older Ansible versions this
functionality works correctly on Ansible 1.8+ or current ``devel`` branch.

2014-11-27
----------

Role updates
~~~~~~~~~~~~

Support for management of SSH host fingerprints in :file:`/etc/ssh/ssh_known_hosts`
(via debops.sshd_ role) and :file:`/root/.ssh/known_hosts` on OpenVZ hosts (via
debops.openvz_ role) has been redesigned and no longer uses ``assemble``
Ansible module. Instead, Ansible checks already present fingerprints and adds
new ones if they are not present in the files. This helps better obfuscate
scanned hosts, which previously could be inferred from filenames of parts
assembled earlier.

Instances of ``with_items`` using multiple lists in a few roles have been
replaced with ``with_flattened`` which works better in new release of Ansible,
1.8+.

debops.openvz_ role has been slightly updated and redundant configuration of
:program:`ferm` and :command:`sysctl`, already configured by debops.ferm_ role, has been
dropped to prevent duplication.

2014-11-26
----------

Role updates
~~~~~~~~~~~~

debops.nginx_ role will now preserve the status for ``default_server`` of
a particular configuration file in case that another instance of the role is
added in the Ansible run. Saved local fact about which server is the default
one will take precedence over automatically calculated setting.

If :program:`nginx` role notices that Ansible local facts are missing, it will remove
all files and symlinks from :file:`/etc/nginx/sites-enabled/` directory. This
should happen in two instances - either :program:`nginx` is configured for the first
time, or :file:`/etc/ansible/facts.d/nginx.fact` file has been removed. In that
case all active config symlinks will be removed to prevent accidental errors
from some old, not regenerated configuration files.

2014-11-25
----------

New roles
~~~~~~~~~

- debops.hwraid_ is a role that configures access to `HWRaid`_ package
  repository and installs packages for recognized RAID storage arrays connected
  to your hosts. It can be used to quickly and easily setup basic monitoring
  for your storage - many packages contain automated scripts which send mail to
  ``root`` account in case of issues with RAID.

Role updates
~~~~~~~~~~~~

debops.auth_ role will now manage :file:`/etc/ldap/ldap.conf` configuration file.
By default, LDAP server on local domain is set up (currently without any
encryption, so treat this as experimental feature and don't use it in
production) with local domain specified as BaseDN. you can change this in role
default variables.

DebOps will automatically configure ``hidepid=2`` option in :file:`/proc`
filesystem on selected hosts (hardware servers and fully virtualized VMs),
using debops.console_ role. This functionality hides other users' process
information for unprivileged accounts. A separate system group, ``procadmins``
has been reserved for monitoring services and users that need full access to
the :file:`/proc` filesystem.

2014-11-24
----------

New roles
~~~~~~~~~

- debops.slapd_ role manages OpenLDAP server, ``slapd``. At the moment role
  is in beta stage - currently there is no SSL encryption available, no
  backup/restore scripts and no replication. But role installs a few useful
  scripts and ``slapd`` management is done using custom Ansible modules.
  Deeper integration between OpenLDAP and other DebOps services will be created
  in the future.

Role updates
~~~~~~~~~~~~

Because of recent changes in the debops.tcpwrappers_ role I decided to make the
ferm rules for SSH access more strict. From now on, :command:`iptables` will
check new SSH connections over period of 1 hour, if more than 3 new connections
from 1 IP address are attempted during that time, and address is not in the
whitelist, it will be blocked for 2 hours, with each new connection attempt
resetting the timer. All this is now configurable in debops.sshd_  and
debops.ferm_ roles.

Thanks to `htgoebel's suggestion`_ I was able to refactor Postfix hash tables
management. They are now generated from all ``*.in`` files in current
directory, which means that other Ansible roles or even other scripts can put
their own files in :file:`/etc/postfix/hash_*/` directories and if they are named
with ``*.in`` extension, their corresponding ``*.db`` files will be created
automatically. Thanks to that, debops.postfix_ role now generates tables from
templates using ``with_fileglob`` instead of static lists of templates, which
makes the process of adding new tables if necessary much easier.

2014-11-22
----------

Role updates
~~~~~~~~~~~~

You can now specify default value for entries in debops.tcpwrappers_ role,
using ``item.default`` key. If this key is specified, and ``item.clients`` is
not present or is empty, default value will be used instead. Specify ``'ALL'``
to allow connections from any host.

Consequently, debops.sshd_ role now will allow connections from any host by
default in :file:`/etc/hosts.allow`. If you previously used a list of hosts using
``sshd_*_allow``, your configuration shouldn't be affected.

2014-11-20
----------

Role updates
~~~~~~~~~~~~

debops.ifupdown_ will now check if previous network configuration in
:file:`/etc/network/interfaces` was using static IP addresses, which indicates that
DHCP is not available on the network. In that case, a basic static IPv4
interface configuration will be used with information gathered by Ansible to
setup a default network interface. This should prevent sudden loss of
communication in cases where hosts are configured statically.

Playbook updates
~~~~~~~~~~~~~~~~

:file:`tools/hostname.yml` playbook has been renamed to :file:`tools/fqdn.yml` and can
get the new hostname and domain from ``fqdn`` variable defined in inventory,
which is less awkward to use than renaming the host in inventory file directly.

2014-11-19
----------

Role updates
~~~~~~~~~~~~

Network forwarding configuration in :command:`iptables` has been moved from
debops.kvm_, debops.lxc_ and ``debops.subnetwork`` roles into debops.ferm_
to avoid duplication. This will also result in forwarded network interfaces
being able to accept Router Advertisements and configure their IPv6 addresses
using SLAAC. In short, easier network configuration.

`Hartmut Goebel`_ has provided a set of `Raspbian`_ APT repositories for
debops.apt_ role, thanks! Unfortunately, at the moment Ansible does not
correctly recognize Raspian as a separate distribution which prevents automatic
source selection, but there are workarounds.

Because of the recent Debian Jessie freeze, DebOps project is starting
preparations for full Jessie support, both as a standalone install, as well as
an upgrade from Wheezy.

All debops.ferm_ configuration files had changed ownership from
``root:root`` to ``root:adm`` which is the default in Debian. This change
should prevent back-and-forth changes of ownership after system has been
upgraded, which forces :program:`ferm` files to change ownership to ``root:adm``.

Some APT configuration files in debops.apt_ role have been renamed to avoid
conflicts with existing files during the upgrade, this should prevent
``debconf`` questions about replacing modified configuration files.

Both debops.apt_ and debops.lxc_ roles now support
``ansible_distribution_release`` in ``'release/sid`` format, which lets DebOps
function correctly on Jessie during the freeze. There might be other roles
which need to be updated to support this syntax, they will be fixed later.

debops.auth_ role now uses full templates instead of ``lineinfile`` module to
configure :command:`sudo` and ``su`` admin access. This should prevent ``debconf``
asking about modifications in :file:`/etc/pam.d/su` (which is now diverted), and
lets :command:`sudo` have more configuration options for ``admins`` group.

Playbook updates
~~~~~~~~~~~~~~~~

New playbook, :file:`tools/hostname.yml` can be used to change the hostname and
FQDN of a host to those defined in Ansible inventory (and yes, you can do
multiple hosts at once). It's advised to not do it after services have been
configured, since some of them may rely on the correct FQDN defined in DNS. If
you use DHCP to automatically configure DNS (for example with ``dnsmasq``,
rebooting the host after changing the hostname should ensure that the new FQDN
is correct.

2014-11-13
----------

Role updates
~~~~~~~~~~~~

debops.postfix_ role will now correctly work on hosts without FQDN
configured. On these hosts, Postfix will automatically override its configured
capabilities and enable local mail delivery, mail will be originating from the
host instead of the domain. Postfix role will also no longer modify
:file:`/etc/hosts` to rewrite IPv6 ``localhost`` address, it seems that the
annoying warning in the mail log about unknown connection source has been
fixed.

debops.dnsmasq_ role has been completely rewritten and now supports multiple
network interfaces and IPv6, among other things. It requires ``ipaddr()``
filter plugin to work, but thanks to that it can automatically configure
services based on IP addresses configured on specified interface - no more
separate IP subnet configuration is needed. Role now also creates more
fine-grained CNAME records and has more configuration options.
And it's out of beta! :-)

Playbook updates
~~~~~~~~~~~~~~~~

Old 'debops.nat' role has been obsoleted by ``debops.subnetwork`` and removed
from :command:`ansible-galaxy` requirements file. It will also be removed from GitHub
and Ansible Galaxy in the future. Also, debops.radvd_ has been added to the
requirements.

Virtualization playbook has been modified and roles that previously
automatically configured internal network and DNS services have been removed
from KVM and LXC plays (yes, this will change installation procedures in the
docs, which are not yet updated). New playbook, 'networking.yml' has been added
where you will find all network-related plays, like subnet creation and
management (via ``debops.subnetwork`` and DHCP/DNS management.

2014-11-07
----------

New roles
~~~~~~~~~

``debops.subnetwork`` is a replacement for old debops.nat_ role, with many
improvements. You can create a bridge interface with local network behind it
for virtual machines, or even switch to a real Ethernet interface for your
physical hosts. You can create both an IPv4 network, which will be
automatically configured behind NAT, and an IPv6 network (with multiple
prefixes). ``debops.subnetwork`` is not yet part of the main playbook, it will
replace the old NAT role when ``dnsmasq`` role is updated to support it.

Role updates
~~~~~~~~~~~~

Because of the changes related to new networking, some code in debops.lxc_,
debops.kvm_ and debops.nat_ had to be moved around. Specifically, parts of
the firewall and sysctl settings related to the LAN interface were moved into
``debops.subnetwork`` role and parts of the forwarding configuration to external
and internal networks were added respectively to LXC and KVM roles.

2014-11-05
----------

New playbooks
~~~~~~~~~~~~~

New playbook has been added, :file:`net/ipv6/6to4.yml`. This playbook configures
`6to4 tunnel`_ interface on a host with public IPv4 address and allows you to
easily connect to IPv6 network. To do that, you need to put a host in
``[debops_6to4]`` group. Afterwards, you can run the playbook using ``debops``
script::

  debops net/ipv6/6to4 -l host

This is first step towards transition to playbooks placed in subdirectories.
These playbooks will probably work correctly only with ``debops`` script, which
automatically generates ``ansible.cfg`` with correct configuration parameters.
To use these playbooks standalone, you will need to create your own
``ansible.cfg`` and include in it paths to DebOps roles and plugins.

Role updates
~~~~~~~~~~~~

You can now configure custom `ferm`_ rules using a ``custom`` template in
debops.ferm_. New ``ferm_*_rules`` variables allow you to create rules in
:file:`/etc/ferm/ferm.d/` directory which can configure tables and chains other
than ``INPUT``.

2014-11-04
----------

New roles
~~~~~~~~~

Finally, it's time to start bringing out new toys. :-) For starters,
debops.radvd_ role, which installs and lets you configure ``radvd``, IPv6
Router Advertisement daemon. It will be used in future IPv6 router roles.

Playbook updates
~~~~~~~~~~~~~~~~

``ipaddr()`` filter has been rewritten again and it works now correctly with
lists of values. Filter was completely refactored internally and its output
should be now consistent with expectations. Hopefully for the last time.

2014-11-02
----------

Playbook updates
~~~~~~~~~~~~~~~~

More fixes in filters! ``split()`` filter will now handle incorrect input
values gracefully and return them in a list, since output is usually expected
to be a list. If a string cannot be split by specified separator, whole string
will be returned in a list.

``ipaddr('6to4')`` filter has been updated to not convert private IPv4
addresses, since their behavior is unspecified, this way Ansible can easily
determine if a given IPv4 address can be used in ``6to4`` tunnel.

``6to4`` query will also now return proper ``::/48`` subnet instead of a single
IPv6 address, this way a subnet can be further manipulated to for example split
it into smaller ``::/64`` subnets.

New ``ipaddr()`` query type has been added - you can now specify positive or
negative numbers in a query, for example ``{{ '192.168.0.1/24' | ipaddr('-1') }}``
will return last IPv4 address from a specified subnet. It's an easy way to
define DHCP dynamic ranges in ``dnsmasq`` configuration.

New filter, ``ipsubnet()`` has been added. It lets you manipulate IPv4 and IPv6
subnets; given a subnet and CIDR prefix you can check the number of subnets
that it can be divided into, adding an index number to the query lets you get
a specific subnet. You can also check the biggest subnet an address can be in
by specifying the smallest prefix you're interested in.

You can now pass a list to ``ipaddr()`` filter and it will return only items
that pass specified criteria, for example returns only list of IP addresses and
subnets by default, or only IPv6 addresses and subnets, etc. It's not yet 100%
correct all the time and not all queries work (or make sense in this context).

2014-10-31
----------

Playbook updates
~~~~~~~~~~~~~~~~

New filter, ``split()`` has been added into filter plugins. It lets you split
strings into a list on a specified separator (by default, space). I'm amazed it
hasn't been included yet in core Ansible. :-) ``split()`` filter has been
written by Tim Raasveld and is included with his blessing, thanks!

``ipaddr()`` filter will from now on correctly handle false values like
``False`` and ``""`` by returning ``False`` when encountered. It also gained
new query type, ``'6to4'`` which lets you convert public IPv4 addresses into
`6to4`_ IPv6 addresses or check if a specified IPv6 address/network is in
``2002::/16`` address range.

2014-10-28
----------

Role updates
~~~~~~~~~~~~

APT repository management in debops.apt_ role has been rewritten. Now role
supports multiple APT mirrors, as well as custom lists of repositories
dependent on the current distribution (repository lists for Debian and Ubuntu
are included). Configuration of default APT repositories has been moved from
a separate config file in :file:`/etc/apt/sources.list.d/` directly to
:file:`/etc/apt/sources.list`, original configuration file is preserved using
:command:`dpkg-divert`. Additionally, if debops.apt_ cannot recognize current
distribution, it won't modify the default ``sources.list`` file, this can also
be enforced manually if needed.

2014-10-17
----------

Role updates
~~~~~~~~~~~~

Many more roles have now partial or full tests on `Travis-CI`_, more to come.

Default version of `Etherpad`_ installed by debops.etherpad_ role has been
changed from ``1.4.0`` to ``develop``, because current stable release does not
recognize new ``npm`` installed in Debian. It will be switched to the next
stable release when it's available.

Because of the recent IPv6 changes in debops.nginx_, management of :program:`nginx`
configuration and daemon had to be changed slightly. Role will try to
automatically pick a sane server as the "default server", if none are marked as
one, due to ``ipv6only=off`` parameter tied to ``default_server`` parameter.
Another added functionality is full nginx server restart when configuration
symlinks in :file:`/etc/nginx/sites-enabled/` directory are added or removed - this
should help with requirement to restart the service on interface changes.

Default admin username and SSH keys are now exposed as :file:`defaults/` variables
in debops.openvz_ role; SSH keys are also sourced from :command:`ssh-agent` instead
of directly from the ``~/.ssh/id_rsa.pub`` file.

2014-10-10
----------

Playbook updates
~~~~~~~~~~~~~~~~

`Maciej Delmanowski`_ wrote a set of custom filter plugins for Ansible which
let you manipulate IPv4 and IPv6 addresses. You can test if a string is a valid
IP address or convert them between various formats.

2014-10-09
----------

Role updates
~~~~~~~~~~~~

IPv6 firewall has been enabled by default in debops.ferm_ after all roles
that configure :program:`ferm` directly had their configuration files fixed to support
both :command:`iptables` and :command:`ip6tables` commands.

debops.boxbackup_ has been finally converted from a "common" role (run from
:file:`common.yml` playbook) to a group-based role. First host in
``debops_boxbackup`` will be configured as the BoxBackup server and the rest
will be set up as its clients.

2014-10-07
----------

Role updates
~~~~~~~~~~~~

debops.ferm_ role is now IPv6-aware and can generate rules for :command:`iptables`
and :command:`ip6tables` at the same time. The way you use the role as a dependency
hasn't changed at all, so if you use dependent variables in your roles, you
should be fine. However, because some roles are managing their firewall rules
by themselves, IPv6 support is disabled by default - this will change when all
roles are updated to be IPv6-aware.

debops.nginx_ also gained support for IPv6 and will now listen for
connections on both types of networks by default. If you have an already
running nginx server, it will require manual restart for the new configuration
to take effect.

2014-10-05
----------

All role README files have been converted to reStructuredText format.
Unfortunately, `Ansible Galaxy`_ does not support :file:`README.rst` files at this
time, so role information cannot be updated there.

2014-10-02
----------

Role updates
~~~~~~~~~~~~

debops.nginx_ role has been updated. Most changes are either cleanup (change
names of some internal role files, remove unused redundant variables, etc.).

:file:`/etc/nginx/http-default.d/` directory has been renamed to
:file:`/etc/nginx/site-default.d/` which hopefully better shows the purpose of this
directory in relation to nginx server configuration. Old directories haven't
been removed; if you use it, you will need to move the configuration files
manually.

Support for ``map { }`` configuration sections has been added. It works
similarly to upstreams and servers, that means you can define your maps in
hashes and enable them using ``nginx_maps`` list. More information about
`nginx map module`_ can be found at the nginx website.

You can now remove configuration of servers, upstreams and maps from hosts by
adding ``delete: True`` to the configuration hashes.

Old remnants of the ``fastcgi_params`` configuration files are now
automatically removed by the nginx role. This is the second step of the switch
from custom to stock configuration file. Task which removes these old files
will be removed in the future.

2014-09-29
----------

"{{ lookup('file','~/.ssh/id_rsa.pub) }}" considered harmful
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The lookup above is common through Ansible playbooks and examples, and it is
used as a prime method of accessing SSH public keys of current account on
Ansible Controller host to, for example, install them on remote hosts using
``authorized_key`` Ansible module.

However, this is by no means a portable solution. Users can have public SSH key
files with completely different names, or don't even have them at all and
instead use other means of SSH authentication, like GPG keys or smartcards.

Because of that, I'm changing the way that SSH public keys will be accessed by
default in DebOps. For now, only :file:`playbooks/bootstrap.yml` playbook will be
updated (this playbook is used to bootstrap new hosts and get them ready for
Ansible management), changes in other roles will come later. I hope that
authors of other roles will follow suit.

New way of accessing SSH keys will use SSH agent (or its alternatives): instead
of accessing the keys directly, Ansible will request a list of currently
enabled public keys from the SSH agent using ``"{{ lookup('pipe','ssh-add -L') }}"``
lookup. Because that lookup can return an empty value which will not create an
error, you want to safeguard against that in a key configuration task using
``failed_when:`` condition. Look in :file:`playbooks/bootstrap.yml` to see how it's
used with ``authorized_key`` task.

2014-09-22
----------

inventory.secret is renamed to secret
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you use DebOps, or at least some roles from it, you probably are familiar
with debops.secret_ role, which makes handling sensitive and confidential
data easier within Ansible playbooks and roles. I'm mentioning this because
``secret`` variable is used through the DebOps project and this change will
be significant - that's why I want to do it right away instead of changing the
role suddenly some time down the line.

Previously debops.secret_ role created directory for secrets adjacent to the
Ansible inventory directory. Because it was assumed that inventories are kept
in the same directory, debops.secret_ automatically took the name of the
inventory directory and appended ``.secret`` suffix to it, making the resulting
directory :file:`inventory.secret/`.

Now, because each DebOps project lives in its own directory, this feature is no
longer needed. Additionally in the current state secret directory is kind of
a show stopper, interfering for example with ``<Tab>``-completion. Because of
that, I'm changing the "formula" to instead just use the :file:`secret/` directory
by default. It will be still created beside the :file:`inventory/` directory.

All DebOps scripts will be updated at the same time, and should work with new
directory name. However, existing directories will need to be renamed manually,
otherwise DebOps might create new certificates, passwords, etc.

``inventory.secret`` directory becomes ``secret``.

If you use :command:`debops-padlock` script, then ``.encfs.inventory.secret``
directory becomes ``.encfs.secret``.

2014-09-21
----------

Role updates
~~~~~~~~~~~~

- debops.postfix_ has been cleaned up, all Ansible tasks have been rewritten
  from "inline" syntax to YAML syntax. Task conditions have been rearranged,
  now almost all of them can be found in :file:`tasks/main.yml` file instead of in
  the file that are included.

- The way that `Postfix`_ configuration files (``main.cf`` and ``master.cf``)
  are created by Ansible has been changed - instead of templating individual
  pieces on the remote servers and assembling them to finished files,
  configuration file templates are generated on Ansible Controller from parts
  included by Jinja and then templated on the servers as a whole. This makes
  the process much faster and easier to manage.

- Postfix role has gained a new capability, ``archive``. If it's enabled, each
  mail that passes through the SMTP server is blind carbon-copied to a separate
  archive mail account on local or remote SMTP server. This function is
  configured automatically by the role, but can be modified using inventory
  variables. Archive account and/or archive server need to be configured
  separately by the system administrator.

2014-09-19
----------

Role updates
~~~~~~~~~~~~

- debops.postfix_ role has gained support for `SMTP client SASL authentication`_,
  in other words the ability to send mail through remote relay MX hosts with
  client authentication, like public or commercial SMTP servers. You can either
  configure one username/password pair for a specified relayhost, or enable
  sender dependent authentication and specify relayhost, user and password for
  each sender mail address separately. Passwords are never stored in the
  inventory; instead Postfix role uses debops.secret_ role to store user
  passwords securely.

2014-09-18
----------

Role updates
~~~~~~~~~~~~

- debops.kvm_ role has been cleaned up from old and unused code, tasks were
  put in order and list of administrator accounts that should have access to
  ``libvirt`` group changed name from ``auth_admin_accounts`` to ``kvm_admins``
  (Ansible account is enabled automatically).

- debops.lxc_ role has been updated with changes to the LXC 1.0.5 package
  from Debian Jessie (some package dependencies and build requirements were
  changed). You can read more in the `lxc package changelog`_.

2014-09-17
----------

Playbook updates
~~~~~~~~~~~~~~~~

- You can now disable early APT cache update using ``apt_update_cache_early``
  variable from debops.apt_ role. This is useful in rare case when your APT
  mirror suddenly catches fire, and you need to switch to a different one using
  Ansible.

Role updates
~~~~~~~~~~~~

- debops.ferm_ role has gained new list variable,
  ``ferm_ansible_controllers``, which can be used to configure CIDR hostnames
  or networks that shouldn't be blocked by ssh recent filter in the firewall. This
  is useful in case you don't use DebOps playbook itself, which does that
  automatically. In addition, debops.ferm_ saves list of known Ansible
  Controllers using local Ansible facts, and uses it to enforce current
  configuration.

- similar changes as above are now included in debops.tcpwrappers_ role, you
  can specify a list of Ansible Controllers in
  ``tcpwrappers_ansible_controllers`` list variable.

- `Debian bug #718639`_ has been fixed which results in changes to several
  configuration files, including :file:`/etc/nginx/fastcgi_params` and inclusion of
  a new configuration file :file:`/etc/nginx/fastcgi.conf`. debops.nginx_ role
  will now check the version of installed :program:`nginx` server and select correct
  file to include in PHP5-based server configuration.

2014-09-14
----------

- Start of a new, separate changelog for DebOps_ playbooks and roles. This is
  a continuation of `previous Changelog`_ from `ginas`_ project.

- all DebOps roles have been moved to `Ansible Galaxy`_ and are now available
  via :command:`ansible-galaxy` utility directly. You can also browse them on the
  `DebOps Galaxy page`_

New roles
~~~~~~~~~

- debops.elasticsearch_ is a role written to manage `Elasticsearch`_
  clusters, either standalone or on multiple hosts separated and configured
  using Ansible groups. Author: `Nick Janetakis`_.

- debops.golang_ role can be used to install and manage `Go language`_
  environment. By default it will install packages present in the distribution,
  but on Debian Wheezy a backport of ``golang`` package from Debian Jessie can
  be automatically created and installed.

Role updates
~~~~~~~~~~~~

- debops.ruby_ role has changed the way how different Ruby versions can be
  selected for installation. By default, ``ruby_version: 'apt'`` variable tells
  the role to install any Ruby packages available via APT (by default 1.9.3
  version will be installed on most distributions). If you change the value of
  ``ruby_version`` to ``'backport'``, a backported Ruby 2.1 packages will be
  created if not yet available, and installed.

- Also in debops.ruby_, ``rubygems-integration`` package is installed
  separately from other packages and can be disabled using
  ``ruby_gems_integration: False`` variable (this option was required for
  backwards compatibility with `Ubuntu 12.04 LTS (Precise Pangolin)`_
  distribution).

.. _Ansible LDAP modules: https://bitbucket.org/psagers/ansible-ldap
.. _commit message: https://github.com/debops/ansible-gitlab_ci/commit/64eb393569267f4eebd9264580d9c1fa22dc32e0
.. _CVE-2013-4547: https://security-tracker.debian.org/tracker/CVE-2013-4547
.. _Debian Bug #630625: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=630625
.. _Debian bug #718639: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=718639
.. _Hartmut Goebel: https://github.com/htgoebel
.. _htgoebel's suggestion: https://github.com/debops/ansible-postfix/issues/11#issuecomment-64113942
.. _latest commit: https://github.com/debops/ansible-gitlab_ci_runner/commit/b46089356e48b4f6719fd9eb64a5684ed0d55ae3
.. _lxc package changelog: http://metadata.ftp-master.debian.org/changelogs/main/l/lxc/testing_changelog
.. _Maciej Delmanowski: https://github.com/drybjed/
.. _Nick Janetakis: https://github.com/nickjj
.. _previous Changelog: https://github.com/ginas/ginas/blob/master/CHANGELOG.md
.. _separate dist-upgrade label: https://github.com/debops/debops-playbooks/labels/dist-upgrade
.. _SMTP client SASL authentication: http://www.postfix.org/SASL_README.html#client_sasl
.. _Travis-CI: https://travis-ci.org/
.. _with_lists plugin: https://github.com/debops/debops-playbooks/blob/master/playbooks/lookup_plugins/lists.py
