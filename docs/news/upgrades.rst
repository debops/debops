.. _upgrade_notes:

Upgrade notes
=============

This document contains information and notes about any changes that are
required in the Ansible inventory or the IT infrastructure managed by DebOps to
perform the upgrades between different stable releases.


Unreleased
----------

Nothing new yet.


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
