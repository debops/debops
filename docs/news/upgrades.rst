.. _upgrade_notes:

Upgrade notes
=============

This document contains information and notes about any changes that are
required in the Ansible inventory or the IT infrastructure managed by DebOps to
perform the upgrades between different stable releases.


Unreleased
----------

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


v0.6.0
------

This is an initial release based off of the previous DebOps roles, playbooks
and tools located in separate :command:`git` repositories. There should be no
changes needed between the old and the new infrastructure and inventory.
