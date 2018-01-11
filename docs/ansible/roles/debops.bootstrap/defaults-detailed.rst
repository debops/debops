Default variable details
========================

Some of ``debops.bootstrap`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _bootstrap__ref_admin_users:

bootstrap__admin_users
----------------------

The :envvar:`bootstrap__admin_default_users` and :envvar:`bootstrap__admin_users` lists
specify what admin accounts will be created by the ``debops.bootstrap`` role.

Most of the existing user accounts attributes will not be modified, unless
specific parameters are explicitly set in an user entry.

New and existing user accounts will be added to the system groups specified in
the :envvar:`bootstrap__admin_groups` list. If SSH public keys are set, they will be
added to user accounts as well.

Each entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the user account to create/manage.

``system``
  Optional, boolean. If specified and ``True``, new user accounts will be
  created as "system" accounts with UID/GID < 1000. If ``False``, new user
  accounts will be "normal" user accounts with UID/GID >= 1000. Existing user
  accounts are not modified.

  If this parameter is not set, :envvar:`bootstrap__admin_system` takes precedence.

``groups``
  Optional. List of system groups which a given user account should belong to.

  If this parameter is not set, :envvar:`bootstrap__admin_groups` takes precedence.

``comment``
  Optional. A comment or GECOS field set for a particular user. If it's not
  specified, the current GECOS field will be preserved on existing accounts. On
  new user accounts, :envvar:`bootstrap__admin_comment` variable will be set.

``home``
  Optional. Home directory path of a given user account. If it's not set, the
  current ``$HOME`` directory of an existing user account will be preserved. On
  new user accounts, the home directory depends on the account status:

  - if it's a "normal" account, its home directory will be located in :file:`/home`
    and named after the user account name.

  - if it's a "system" account, its home directory will be located in
    :file:`/var/local` and named after the user account name.

``shell``
  Optional. The default shell executed on login. If not specified, the current
  shell will be preserved on existing user accounts. On new accounts,
  :envvar:`bootstrap__admin_shell` variable takes precedence.

``home_group``
  Optional. If set, the home directory group of a given user account will be
  set to this group. If not set, home directories of existing accounts won't be
  modified. New accounts will have their home directory group set to the value
  of :envvar:`bootstrap__admin_home_group` variable.

``home_mode``
  Optional. If set, the home directory of a given user account will have the
  specified permissions. If not set, the home directories of existing user
  accounts won't be modified. New accounts will have their home directories
  permissions set based on the :envvar:`bootstrap__admin_home_mode` variable.

``sshkeys``
  Optional. List of SSH public keys to set on an account. This list will be
  combined with list of keys set in :envvar:`bootstrap__admin_sshkeys` variable.


Examples
~~~~~~~~

Create two user accounts with default settings, one of which is created only on
Ubuntu hosts:

.. code-block:: yaml

   bootstrap__admin_users:

     - name: 'ansible'

     - '{{ {"name": "ubuntu"}
            if ansible_distribution == "Ubuntu"
            else {} }}'
