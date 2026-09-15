.. Copyright (C) 2023 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.borgbackup`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _borgbackup__ref_encryption:

borgbackup__encryption
----------------------

The :envvar:`borgbackup__encryption` variable defines the encryption mode to
use for newly created repositories (once created, this cannot be changed).
Currently valid modes for :command:`borg` version 1.2.x include
``keyfile``/``repokey`` (SHA-256, stored locally or in the repo) and
``keyfile-blake2``/``repokey-blake2``.

For a full list of possible encryption modes, consult the
`upstream documentation`__ (make sure that you read the documentation for the
right version of :command:`borg`, as the modes can and will change between
versions).

.. __: https://borgbackup.readthedocs.io/en/stable/usage/init.html#more-encryption-modes

By default, a random passphrase will be generated and stored on the controller
and copied to the host. On systems using :command:`systemd`, this key will be
encrypted using :man:`systemd-creds(1)`, using a host-specific key and the
host's TPM2 chip (if available). The passphrase will be automatically decrypted
and passed to :command:`borgmatic` when the :file:`borgmatic.service` unit is
started (typically via the :file:`borgmatic.timer` unit).

On non-systemd system, the passphrase will be stored in a plaintext file in
the :file:`/etc/borgmatic/passphrases` directory and protected by file
permissions.

The passphrase is used during repository creation to encrypt a newly generated
"borg key" (a `set of keys`__ used to encrypt and sign backups). The borg key
is stored in the :file:`/root/.config/borg/keys` directory on the host. A copy
of the contents of this directory will also be stored on the controller.

Note that the above configuration means that repo access requires *both* the
borg key and the passphrase.

.. __: https://borgbackup.readthedocs.io/en/stable/internals/data-structures.html#key-files


.. _borgbackup__ref_server_accounts:

borgbackup__server_accounts
---------------------------

The ``borgbackup__server_*_configuration`` :ref:`universal_configuration`
variables are used to configure borg SSH users on a server via the
:ref:`debops.users` and :ref:`debops.authorized_keys` roles.


Syntax
~~~~~~

``name``
  Required. The name of the user account to be created.
  This name will feature as part of the connection string to the repo.

``clients``
  Required. List of inventory-managed borg client host shortnames.

  Either this or ``sshkeys`` need to have at least one entry.

  Hosts listed here will get their root public key added automatically by
  accessing the server's ``root_account.ssh_public_key`` fact.

``sshkeys``
  Required. List of ssh public keys to authorize access for.

  Either this or ``clients`` need to have at least one entry.

  Gets passed to ``debops.authorized_keys`` in addition to client entries.

``append_only``
  Optional. Defaults to False.

  Limits the account to ``append_only`` mode. See below for further explanation.

``state``
  Optional. Set this to ``absent`` to remove configuration.
  It's passed directly to the ``users`` and ``authorized_keys`` roles.

``home``
  Optional. If left unset it will default to the system's :file:`/home` dir.

``groups``
  Optional. Allows adding the user to groups *in addition* to the
  ``ansible_local.system_groups.local_prefix + "sshusers"`` group that is added
  by the role for SSH access.

``users_extra``
  Optional. Mapping of values to be passed to :ref:`debops.users` as
  ``users__dependent_accounts`` for the item.

  These will be added to the item definition, allowing adapting the user further.

``authorized_keys_extra``
  Optional. Mapping of values to be passed to :ref:`debops.authorized_keys` as
  ``authorized_keys__dependent_identities`` for the item.

  These will be added to the item definition, allowing adapting the entry further.


.. _borgbackup__ref_append_only:

Append-only mode
~~~~~~~~~~~~~~~~

The ``item.append_only`` variable controls whether clients should be limited to
"append only" access to the account's repositories.

When enabled, clients cannot delete old archives, which protects against
someone gaining access to a client and deleting/overwriting old backups.

The drawback is that the repos will grow indefinitely, and automatic periodic
purging cannot be implemented as that would mean that data marked by a hacked
client as to-be-deleted would automatically be deleted, defeating the purpose
of this setting.

If enabled, the repositories will have to be reviewed for malicious activity
and later purged manually in order to free up space from old archives, e.g. by
running this on the backup server:

.. code-block:: console

   borg check --verify-data <repo>
   borg compact <repo>

For more details, consult the `borgbackup documentation on append-only mode`__.

.. __: https://borgbackup.readthedocs.io/en/stable/usage/notes.html#append-only-mode-forbid-compaction


.. _borgbackup__ref_configuration:

borgbackup__configuration
-------------------------

The ``borgbackup__*_configuration`` variables define configuration files
in borgmatic's configuration directories.

A configuration item's behavior is dictated by its ``type``:

``unit``
  Units are placed in :file:`/etc/borgmatic.d/[name].yaml`,
  where they load in sequence with all other units in the directory when
  :command:`borgmatic` is invoked.

  Unit syntax is validated by borgmatic on upload, although this doesn't
  guarantee that it won't fail when it actually tries to run.

``include``
  Includes are placed in :file:`/etc/borgmatic/[name].yaml`.
  Include files are meant to hold fragments of configuration that may be
  merged into unit files.

  They do not get validated on upload, but their content is taken into account
  when the units that reference them pass validation.

  :file:`config.yaml` from that folder is loaded as a unit file by borgmatic,
  so for clarity the ``config`` name should probably be avoided.

``repo``
  A repo entry will initialize a borg repository with its ``name`` and a passphrase.

  It will produce a regular yaml ``unit``, a systemd credential at
  :file:`/etc/borgmatic/passphrases/` (or plaintext file with cron) and an
  additional include at :file:`/etc/borgmatic/repos/[name].yaml`
  containing its repositories and authentication command.


.. attention::

   Up to version ``1.8.1``, top level includes only accept **a single file**.

   In earlier versions, the role will daisy-chain a **single** supplied include string
   at the top of the repo definition, resulting in the equivalent merge order as an
   ``['include.yaml', 'repo.yaml']`` statement.


See the :ref:`borgbackup__ref_configuration_examples` section in Getting Started
for example usage.


Syntax
~~~~~~

The role uses the :ref:`universal_configuration` system to configure the
:command:`borgmatic` script. Each configuration entry in the list is
a YAML file .

``name``
  Required. Specify the name of the :command:`borgmatic` configuration
  file name/parameter. The names are case-sensitive. The toplevel ``name``
  parameter is used to define the name of the configuration file to generate in
  the :file:`/etc/borgmatic` directory. The filename will automatically include
  a ``.yaml`` suffix, so it should be excluded. Note that it is not possible
  to quote/escape the filename in all role tasks, so the name should be kept
  simple (like ``main``, ``database-3``, ``app-xyz``, etc).

  Multiple configuration entries with the same ``name`` parameter are merged
  together in order of appearance. This can be used to modify parameters
  conditionally.

  An item name that starts with a ``/`` is considered an absolute filename
  to a yaml file. Otherwise names are used to generate filenames according
  to each entry's ``type``.

``type``
  Optional. Defaults to ``unit``.
  Determines the behavior of a configuration entry.

``state``
  Optional. If not specified or ``present``, a given configuration file
  will be present in the generated configuration.
  If ``absent``, the configuration file will be deleted.

  If the state is ``ignore``, a given configuration entry will not be evaluated
  during role execution. This can be used to activate configuration entries
  conditionally.

``comment``
  Optional. A string containing a comment for a given parameter.

``path``
  Optional. Allows overriding a configuration's output file path with an
  absolute filename. This can be useful for placing configuration units outside
  of borgmatic's load path, to be manually loaded with ``borgmatic --config [file]``

``include``
  Optional. Configures a *top level include* line at the beginning of the
  configuration file. Accepts a string or a list of strings.

  Short names are resolved to the particular include's filepath, while
  absolute filenames (starting with a ``/``) are used as provided.

  Each ``yaml`` file config may only have a single top level include, although
  versions ``1.8.1`` and later of borgmatic allow a list of files to be provided
  as its value.

``yaml``
  Optional. Extra yaml to include in the generated config file.

  This is the pretty syntax for writing simple definitions in inventory.
  It renders the mapping provided ``to_nice_yaml``.

``raw``
  Optional. Raw text to include in the yaml document.

  Will be rendered as-is at the end of the document, after the ``yaml`` content.
