Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.users`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1

.. _users__ref_groups:

users__groups
-------------

The :envvar:`users__groups`, :envvar:`users__group_groups` and :envvar:`users__host_groups` lists
can be used to manage UNIX groups on remote hosts using Ansible inventory. Each
list entry is a YAML dictionary that describes the state and parameters of
a given group. The group definition is a subset of the user definition
described below, and some parameters are shared in both cases.

List of known parameters:

``group`` or ``name``
  Required. Name of the UNIX group to manage. If ``group`` is not specified,
  ``name`` will be used automatically.

``system``
  Optional, boolean. If ``True``, a given group will be a "system" group, with
  it's GID < 1000. If the value is ``False``, the group will be a "normal"
  group with GID >= 1000.

  If not specified, the :envvar:`users__default_system` variable will determine the
  group type.

``gid``
  Optional. Specify the GID of the managed UNIX group.

``state``
  Optional. If ``present``, the UNIX group will be created. If ``absent``, the
  specified group will be removed.

Examples
~~~~~~~~

.. literalinclude:: examples/manage-groups.yml
   :language: yaml


.. _users__ref_accounts:

users__accounts
---------------

The :envvar:`users__accounts`, :envvar:`users__group_accounts`, :envvar:`users__host_accounts` as
well as some additional ``users__*_accounts`` lists are used to manage UNIX
user accounts. Each list entry is a YAML dictionary with parameters that define
a particular account.

General account parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

``name``
  Required. Name of the UNIX user account to manage.

``system``
  Optional, boolean. If ``True``, a given user account and primary group will
  be a "system" account and group, with it's UID and GID < 1000. If the value
  is ``False``, the user account and group will be a "normal" account and group
  with UID and GID >= 1000.

  If not specified, the :envvar:`users__default_system` variable will determine the
  account and group type.

``uid``
  Optional. Specify the UID of the UNIX user account.

``gid``
  Optional. Specify the GID of the primary group for a given user account.

``group``
  Optional. Name of the UNIX group which will be set as the primary group of
  a given account. If ``group`` is not specified, ``name`` will be used
  automatically to create the corresponding UNIX group.

``groups``
  Optional. List of UNIX groups to which a given UNIX account should belong.
  Only existing groups will be added to the account.

``append``
  Optional, boolean. If ``True`` (default), the specified groups will be added
  to the list of existing groups the account belongs to. If ``False``, all
  other groups than those present on the group list will be removed stripped.

``comment``
  Optional. A comment, or GECOS field configured for a specified UNIX account.

``shell``
  Optional. Specify the default shell to run when a given UNIX account logs in.
  If not specified, the default system shell (usually :file:`/bin/sh` will be used
  instead. You can also specify shell for all user accounts managed by this
  role using the :envvar:`users__default_shell` variable.

``password``
  Optional. Specify the encrypted hash of the user's password which will be set
  for a given UNIX account. You can use the ``lookup("password")`` lookup to
  generate the hash. See examples for more details.

``update_password``
  Optional. If set to ``on_create``, the password will be set only one on
  initial user creation. If set to ``always``, the password will be updated on
  each Ansible run if it's different.

  The module default is to always update the password, the ``debops.users``
  default is to only update the password on initial user creation.

``non_unique``
  Optional, boolean. If ``True``, allows setting the UID to a non-unique value.

``linger``
  Optional, boolean. If ``True``, the UNIX account will be allowed to linger
  when not logged in and manage private services via it's own
  :command:`systemd` user instance. If ``False``, the linger option will be
  disabled.

Parameters related to account state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``state``
  Optional. If ``present``, the UNIX user account and primary group will be
  created. If ``absent``, the specified account and group will be removed.

``force``
  Optional, boolean. If used with ``state`` parameter being ``absent``, Ansible
  will execute the ``userdel --force`` command.

``remove``
  Optional, boolean. If used with ``state`` parameter being ``absent``, Ansible
  will execute the ``userdel --remove`` command.

``expires``
  Optional. Specify the time in the UNIX epoch format, at which a given UNIX
  user account will be disabled.

Parameters related to home directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``home``
  Optional. Path to the home directory if a given user account.

``home_owner``
  Optional. Specify the owner of the home directory of a given UNIX account.

``home_group``
  Optional. Specify the group of the home directory of a given UNIX account.

``home_mode``
  Optional. Specify the mode of the home directory of a given UNIX account.

``createhome``
  Optional, boolean. If ``True``, the role will create the home directory for
  a given user account if it doesn't exist already. If not specified, home
  directory is created by default by the `Ansible user module`_.

``move_home``
  Optional, boolean. If ``True`` and the managed user account already exists,
  Ansible will try to move it's home directory to the location specified in the
  ``home`` parameter if it isn't there already.

``skeleton``
  Optional. Specify path to the directory, contents of which will be copied to
  the newly created home directory.

``home_acl``
  Optional. Configure filesystem ACL entries of the home directory of a given
  UNIX user account. This parameter is a list of YAML dictionaries, each
  element uses a specific set of parameters derived from the ``acl`` Ansible
  module, see its documentation for details, as well as the :man:`acl(5)`,
  :man:`setfacl(1)` and :man:`getfacl` manual pages. Some useful parameters:

  ``default``
    Optional, boolean. If ``True``, set a given ACL entry as the default for
    new files and directories inside a given directory. Only works with
    directories.

  ``entity``
    Name of the UNIX user account or group that a given ACL entry applies to.

  ``etype``
    Specify the ACL entry type to configure. Valid choices: ``user``,
    ``group``, ``mask``, ``other``.

  ``permissions``
    Specify the permission to apply for a given ACL entry. This parameter
    cannot be specified when the state of an ACL entry is set to ``absent``.

  ``recursive``
    Apply a given ACL entry recursively to all entities in a given path.

  ``state``
    Optional. If not specified or ``present``, the ACL entry will be created.
    If ``absent``, the ACL entry will be removed. The ``query`` state doesn't
    make sense in this context and shouldn't be used.

Parameters related to the account's private SSH key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``generate_ssh_key``
  Optional, boolean. If ``True``, Ansible will generate a private SSH key for
  the specified account.

``ssh_key_bits``
  Optional. Number of bits to use for the user's private SSH key. If not
  specified, role will use the `Ansible user module`_ default value.

``ssh_key_comment``
  Optional. Add a custom comment to the generated SSH key.

``ssh_key_file``
  Optional. Path where the private SSH key will be stored.

``ssh_key_passphrase``
  Optional. Set a passphrase which will be required to decrypt the private SSH
  key.

``ssh_key_type``
  Optional. Specify the SSH key type to generate. If not specified, RSA keys
  will be generated automatically.

Parameters related to public SSH keys
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sshkeys``
  Optional. String or a YAML list of public SSH keys to configure for a given
  user account. The keys will be stored in the ``~/.ssh/authorized_keys``
  file.

``sshkeys_exclusive``
  Optional, boolean. If ``True``, the role will remove all keys from the user's
  ``~/.ssh/authorized_keys`` file that are not specified in the ``sshkeys``
  parameter.

``sshkeys_state``
  Optional. If not specified or ``present``, the SSH keys will be set on the
  user's account. If ``absent``, the ``~/.ssh/authorized_keys`` file will be
  removed entirely.

Parameters related to mail forwarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``forward``
  Optional. String or YAML list of e-mail addresses which will be used to
  forward mail directed to a given UNIX account. They will be stored in the
  ``~/.forward`` file. This is only valid for MTAs that support this mechanism,
  for example Postfix MTA when local mail is enabled.

``forward_state``
  Optional. If not specified or ``present``, the e-mail addresses specified in
  the ``forward`` parameter will be added to the ``~/.forward`` configuration
  file. If ``absent``, the entries will be removed from the configuration file.

Parameters related to user configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``dotfiles_enabled``
  Optional, boolean. Enable or disable management of the user configuration
  files.

``dotfiles_name``
  Optional. Name of the key in the :envvar:`users__dotfiles_combined_map` dictionary
  which corresponds to the user configuration files to use. If not specified,
  the default from :envvar:`users__dotfiles_name` will be used.

You can also use the parameters below to configure the dotfiles directly for
a specific account.

``dotfiles_repo``
  Optional. URL to the :command:`git` repository with the user configuration files to
  deploy. If not specified, the default dotfiles repository will be used
  instead.

``dotfiles_dest``
  Optional. Specify the path where the user configuration files should be
  cloned into. If not specified, :envvar:`users__dotfiles_dest` variable will be used
  instead, by default cloning the :command:`git` repository to :file:`~/.config/dotfiles/`
  directory.

``dotfiles_version``
  Optional. Specify a :command:`git` branch or tag  of the user configuration
  files which should be downloaded and checked out. If not specified, role will
  automatically check out the ``master`` branch.

``dotfiles_update``
  Optional, boolean. Specify if the user configuration files repository should
  be updated on each Ansible run. If not set, the default from
  :envvar:`users__dotfiles_update` will be used instead.

``dotfiles_command``
  Optional. Command to execute to deploy the dotfiles. The command will be
  executed in the checked out directory (by default :file:`~/.config/dotfiles/`)
  with the user privileges.

  The task checks the output of the given command; if it's not empty, the task
  will be marked as changed.

``dotfiles_creates``
  Optional. Path to a file which indicates that the dotfiles deployment has
  been completed and the command task will be skipped. If not specified, the
  command used to deploy the configuration files will be executed on each
  Ansible run.

Examples
~~~~~~~~

.. literalinclude:: examples/manage-accounts.yml
   :language: yaml


.. _users__ref_resources:

users__resources
----------------

The :envvar:`users__resources`, :envvar:`users__group_resources` and
:envvar:`users__host_resources` lists can be used to manage directories, files
and symlinks for specific UNIX accounts using Ansible inventory. This
functionality is meant to be used to manage small amounts of data, like custom
configuration files, private SSH keys and so on. For more advanced management,
you should consider using debops.resources_ Ansible role, or even writing
a custom Ansible role from scratch.

Tasks that manage the resources are executed with the privileges of a specific
user account; this account should exist (presumably it was created by the role
earlier). This allows the usage of ``~/`` in the paths to manage directories
and files relative to the user's ``$HOME`` directory.

Each entry on the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the user account which will be used to run the Ansible
  tasks using the "become" method.

``state``
  Required. This variable defines the resource state and it's type:

  - ``absent``: the resource will be removed
  - ``directory``: the resource is a directory
  - ``file``: the resource is a file
  - ``link``: the resource is a symlink
  - ``touch``: the resource will create an empty file, or "touch" an existing
    file on each Ansible run

  If this parameter is not specified, the resource will be treated as
  a directory.

``dest`` or ``path``
  Required. Path to the resource managed by this entry. Usually you want to
  specify it as relative to the user's ``$HOME`` directory.

``src``
  If the resource type is a ``link``, this parameter specifies the target of
  the symlink.

  If the resource type is a ``file``, this parameter can be used to specify the
  source file on the Ansible Controller to copy to the remote host. It
  shouldn't be specified together with the ``content`` parameter.

``content``
  If the resource type is a ``file``, this parameter can be used to specify the
  contents of the file that is managed by this entry, usually in the form of
  a YAML text block. It shouldn't be specified together with the ``src``
  parameter.

``force``
  Optional, boolean. If ``True``, the files will be always overwritten, if
  ``False``, files will be copied only if they don't exist. This parameter can
  also be used to force creation of symlinks.

``mode``
  Optional. Set specific permissions for a given file/directory/symlink.

``recurse``
  Optional, boolean. Recursively set specified permission for all directories
  in the directory tree that lead to a given directory/file, depending on user
  privileges.

``parent``
  Optional, boolean. If ``True`` (default), the role will create the parent
  directories of a given resource as needed, depending on the privileges of
  a given user account. If ``False``, role will not try to create the missing
  directories.

``parent_mode``
  Optional. Specify the permissions of the parent directory of a given
  file resource.

``parent_recurse``
  Optional, boolean. If ``True``, parent permissions will be applied
  recursively to all parent directories.

Examples
~~~~~~~~

.. literalinclude:: examples/manage-resources.yml
   :language: yaml


.. _users__ref_dotfiles_map:

users__dotfiles_map
-------------------

This is a YAML dictionary which can be used to define sets of user
configuration files. These sets can then be enabled globally or per user
account as needed. Each set is a YAML dictionary with specific parameters:

``repo``
  Required. An URL to the :command:`git` repository which holds the user configuration
  files.

``command``
  Optional. A command executed by Ansible used to deploy the dotfiles. The
  command will be executed with a given user privileges, in the dotfiles
  directory (by default :file:`~/.config/dotfiles/`).

``creates``
  Optional. Path to the file which will indicate that the dotfiles have been
  deployed. If not specified, the command set in the ``command`` parameter will
  be executed on each Ansible run.

``shell``
  Optional. Specify the shell which should be enabled for users that use
  a given set of user configuration files.

Examples
~~~~~~~~

.. literalinclude:: examples/manage-dotfiles.yml
   :language: yaml
