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


.. _borgbackup__ref_append_only:

borgbackup__append_only
-----------------------

The :envvar:`borgbackup__append_only` variable controls whether clients should
have "append only" access to remote repositories. When enabled, clients cannot
delete old archives, which protects against someone gaining access to a client
and deleting/overwriting old backups.

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

For more details, consult the `borgbackup documentation`__.

.. __: https://borgbackup.readthedocs.io/en/stable/usage/notes.html#append-only-mode-forbid-compaction


.. _borgbackup__ref_configuration:

borgbackup__configuration
-------------------------

The ``borgbackup__*_configuration`` default variables define the configuration
of the :command:`borgmatic` script which works as a wrapper for the
:command:`borg` software. An online reference for the :command:`borgmatic`
script can be found `here`__, but it might describe a newer version than
that which is installed on the hosts. A commented configuration file for
a given :command:`borgmatic` version can be generated using the
:command:`generate-borgmatic-config --destination /some/path` command
after the :command:`borgmatic` package has been installed.

.. __: https://torsion.org/borgmatic/docs/reference/configuration/

The generated configuration will by default be located at
:file:`/etc/borgmatic/config.yaml`.

Examples
~~~~~~~~

You can check the :envvar:`borgbackup__original_configuration` variable for the
default (long) contents of the configuration file.

Syntax
~~~~~~

The role uses the :ref:`universal_configuration` system to configure the
:command:`borgmatic` script. Each configuration entry in the list is
a YAML dictionary. The simple form of the configuration uses the dictionary
keys as the parameter names, and dictionary values as the parameter values.
Remember that the parameter names are case sensitive, and it is recommended
to use a single YAML dictionary per configuration option.

If the YAML dictionary contains the ``name`` key, the configuration switches to
the complex definition mode, with configuration options defined by specific
parameters:

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

``option``
  Optional. A string describing the name of a given parameter should have in
  the generated configuration file instead of ``name``. This can be used to
  e.g. provide alternative options with the same ``option`` but different
  ``name`` values (to avoid the parameters being merged).

``options``
  Optional. A list of configuration options that belong to a given
  file/section. Needs to be defined as a nested list of YAML dictionaries.

``comment``
  Optional. A string containing a comment for a given parameter.

``value``
  Required. The value of a given configuration option. It can be a string,
  number, ``True``/``False`` boolean, list of strings, or an empty string.

``state``
  Optional. If not specified or ``present``, a given configuration parameter
  will be present in the generated configuration file. If ``absent``, a given
  parameter will be removed from the configuration file. If ``comment``, the
  parameter will be present but commented out.

  If the state is ``init``, the parameter will be "primed" in the configuration
  pipeline, but it will be commented out in the generated configuration file.
  Any subsequent configuration entry with the same ``name`` will switch the
  state to ``present`` - this is used to define the default parameters in the
  role which can be changed via the Ansible inventory.

  If the state is ``ignore``, a given configuration entry will not be evaluated
  during role execution. This can be used to activate configuration entries
  conditionally.
