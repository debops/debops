.. _users__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
changelog for more details about what has changed.


From v0.1.x to v0.2.x
---------------------

All role variables have been renamed from ``users_*`` to ``users__*`` to move
them to a separate namespace.

List of renamed user list variables:

+----------------------+-----------------------------------+
| Old variable name    | New variable name                 |
+======================+===================================+
| ``users_list``       | :envvar:`users__accounts`         |
+----------------------+-----------------------------------+
| ``users_group_list`` | :envvar:`users__group_accounts`   |
+----------------------+-----------------------------------+
| ``users_host_list``  | :envvar:`users__host_accounts`    |
+----------------------+-----------------------------------+
| ``users_root``       | :envvar:`users__root_accounts`    |
+----------------------+-----------------------------------+
| ``users_admins``     | :envvar:`users__admin_accounts`   |
+----------------------+-----------------------------------+
| ``users_default``    | :envvar:`users__default_accounts` |
+----------------------+-----------------------------------+
| ``users_groups``     | :envvar:`users__groups`           |
+----------------------+-----------------------------------+
|                      | :envvar:`users__group_groups`     |
+----------------------+-----------------------------------+
|                      | :envvar:`users__host_groups`      |
+----------------------+-----------------------------------+

List of other renamed variables:

+--------------------------------+---------------------------------------+
| Old variable name              | New variable name                     |
+================================+=======================================+
| ``users_default_dotfiles``     | :envvar:`users__dotfiles_enabled`     |
+--------------------------------+---------------------------------------+
| ``users_default_dotfiles_key`` | :envvar:`users__dotfiles_name`        |
+--------------------------------+---------------------------------------+
| ``users_dotfiles``             | :envvar:`users__dotfiles_default_map` |
+--------------------------------+---------------------------------------+

This script can come in handy to update the inventory variable names, assuming
that your inventory is stored in a :command:`git` repository:

.. literalinclude:: scripts/upgrade-from-v0.1.x-to-v0.2.x.sh
   :language: shell

The script is bundled with this role under
:file:`docs/scripts/upgrade-from-v0.1.x-to-v0.2.x.sh` and can be invoked from
there.
