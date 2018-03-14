.. _upgrade_notes:

Upgrade notes
=============

This document contains information and notes about any changes that are
required in the Ansible inventory or the IT infrastructure managed by DebOps to
perform the upgrades between different stable releases.


Unreleased
----------

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


v0.7.0
------

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


v0.6.0
------

This is an initial release based off of the previous DebOps roles, playbooks
and tools located in separate :command:`git` repositories. There should be no
changes needed between the old and the new infrastructure and inventory.
