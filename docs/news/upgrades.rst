.. _upgrade_notes:

Upgrade notes
=============

This document contains information and notes about any changes that are
required in the Ansible inventory or the IT infrastructure managed by DebOps to
perform the upgrades between different stable releases.


Unreleased
----------

Subordinate UID/GID ranges for root
-----------------------------------

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
-----------------------------------------------------------

- The :ref:`debops.ifupdown` role now uses :ref:`debops.sysctl` role directly
  as a dependency to generate forwarding configuration for each managed network
  interface that has it enabled. This might impact packet forwarding on
  existing systems; run the role with Ansible ``--diff --check`` options first
  to review the planned changes to the host.

Inventory variable changes
~~~~~~~~~~~~~~~~~~~~~~~~~~

- The :envvar:`bootstrap__etc_hosts` value has been changed from a boolean to
  trinary ``present``/``absent``/``ignore`` to allow conditional removal of
  :file:`/etc/hosts` entries, with ``present`` being the default.

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
  removed from the :ref:`debops.bootstrap` role. The ``bootstrap.yml`` playbook
  now uses the :ref:`debops.sudo` role to configure :command:`sudo` service on
  a host, use its variables instead to control the service in question.

- The :envvar:`bootstrap__admin_groups` variable will now use list of UNIX
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
  :envvar:`nodejs__upstream_release` to better represent the contents, which is
  not a specific NodeJS version, but a specific major release.

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
