Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the Changelog for
more details about what has changed.

From debops.sshkeys to debops.authorized_keys
---------------------------------------------

- The ``debops.authorized_keys`` role supports old variable names used by
  ``debops.sshkeys``. The switch should be without issues. Role might update
  the file ownership and permissions to set the files to read only mode.

- You should update your inventory variables to use the new role variable names:

  +------------------------+---------------------------------+
  | Old variable name      | New variable name               |
  +========================+=================================+
  | ``sshkeys_list``       | ``authorized_keys__list``       |
  +------------------------+---------------------------------+
  | ``sshkeys_group_list`` | ``authorized_keys__group_list`` |
  +------------------------+---------------------------------+
  | ``sshkeys_host_list``  | ``authorized_keys__host_list``  |
  +------------------------+---------------------------------+
