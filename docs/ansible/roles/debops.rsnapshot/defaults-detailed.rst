Default variable details
========================

Some of ``debops.rsnapshot`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _rsnapshot__ref_ssh_identities:

rsnapshot__ssh_identities
-------------------------

The :envvar:`rsnapshot__ssh_default_identities` and
:envvar:`rsnapshot__ssh_identities` variables define the SSH identities
(private/public key pairs) used by the :command:`rsnapshot` script to access
the remote hosts over SSH. The default identities are created on the initial
setup and stored in the :file:`/root/.ssh/` directory, the main identity used
by the role if none is selected is defined by the
:envvar:`rsnapshot__ssh_main_identity` variable. Users can use the
:envvar:`rsnapshot__ssh_identities` variable to add more identities or to
override the default ones if necessary.

The public portion of the SSH keys is accessible via the Ansible local facts,
via the ``ansible_local.rsnapshot.ssh_identities`` dictionary.

Examples
~~~~~~~~

Create a custom SSH identity for older machines, the DSA keys have to use
a length of 1024 bits:

.. code-block:: yaml

   rsnapshot__ssh_identities:

     - name: 'id_rsnapshot_dsa'
       type: 'dsa'
       bits: '1024'

Syntax
~~~~~~

The variables are lists of YAML dictionaries, each dictionary defines a SSH
identity using specific parameters:

``name``
  Required. The name of the SSH identity used as the filename; it's common to
  use the ``id_`` prefix in the SSH key filenames. The name will be used for
  the private key file, public key will have the ``.pub`` suffix added
  automatically. The configuration entries with the same ``name`` parameter are
  merged, this mechanism can be used to modify the SSH identities
  conditionally.

``state``
  Optional. If not specified or ``present``, the SSH identity will be created.
  Currently SSH identities cannot be removed1 by the role, so the ``absent``
  parameter will result in a given identity not being created if it doesn't
  exist. The ``ignore`` value will tell the role to ignore a given
  configuration entry during execution.

``type``
  Optional, name of the SSH key type to create, depending on the support on the
  host. Usually either ``ed25519``, ``rsa`` or ``dsa``. If not specified, the
  value of the :envvar:`rsnapshot__ssh_key_type` will be used by default.

``bits``
  Optional, the size of the generated RSA keys. If it's not specified, the
  value of the :envvar:`rsnapshot__ssh_key_bits` is used by default. Needs to
  be set to ``1024`` for the DSA keys.

``comment``
  Optional. A comment added to the generated SSH identity. If not specified,
  the value of the :envvar:`rsnapshot__ssh_key_comment` will be used by
  default.


.. _rsnapshot__ref_hosts:

rsnapshot__hosts
----------------

The ``rsnapshot__*_hosts`` lists define the configuration of the hosts to back
up by the :command:`rsnapshot` script. Each host configuration is defined as
a YAML dictionary and describes the contents of the
:file:`/etc/rsnapshot/hosts/<name>/` directory. The default configuration is
based on the ``rsnapshot__*_configuration``, ``rsnapshot__*_excludes`` and
``rsnapshot__*_includes`` variables, and can be modified per-host as needed.

Examples
~~~~~~~~

Back up specific hosts defined in the Ansible inventory with default values:

.. code-block:: yaml

   rsnapshot__hosts:

     - 'hostname1'
     - 'hostname2'
     - 'hostname3'

Create backup configuration for hosts in a specific Ansible inventory group:

.. code-block:: none

   # ansible/inventory/hosts

   [hosts_to_backup]
   hostname1
   hostname2
   hostname3

.. code-block:: yaml

   ---
   # ansible/inventory/host_vars/backup-host/rsnapshot.yml

   rsnapshot__hosts:

     - '{{ groups["hosts_to_backup"]
           | difference(groups["debops_service_rsnapshot"]) }}'

Create configuration for host in the Ansible inventory but specify the host's
FQDN directly instead of using Ansible fact gathering to get it. This can be
used to select a different host address than the one Ansible sets as the
``ansible_fqdn`` variable.

This method can also be used to create backup configuration for hosts outside
of the Ansible inventory.

.. code-block:: yaml

   rsnapshot__hosts:

     - name: 'hostname1'
       fqdn: 'host.example.org'

Create backup configuration for an external host that uses non-standard SSH
port and does not support the ``ed25519`` SSH keys, only RSA. This is also an
OpenVZ container which cannot modify the I/O niceness using the
:command:`ionice` command, therefore the command defined in the SSH key
installed on the host needs to be different:

.. code-block:: yaml

   rsnaphot__hosts:

     - name: 'old-db.example.org'
       ssh_port: 2200
       ssh_identity: 'id_rsnapshot_rsa'
       ssh_command: 'nice /usr/local/bin/rrsync -ro /'

Create configuration for an external host but don't install the SSH key (it
will be installed manually out-of-band). Exclude any NFS mounts inside of the
home directories from backups.

.. code-block:: yaml

   rsnapshot__hosts:

     - name: 'appserver.example.org'
       ssh_key: False
       excludes:
         - '/home/*/nfs'

Create backup configuration for a host in the Ansible inventory, but make
snapshots in a removable media storage and don't create the snapshot directory
automatically if it's not present (removable media is removed):

.. code-block:: yaml

   rsnapshot__hosts:

     - name: 'hostname2'
       options:

         - snapshot_root: '/media/USB0/Snapshots/hostname2'
         - no_create_root: 1

Create backup of the local host based on its inventory name (this is enabled by
default in the :envvar:`rsnapshot__default_hosts` variable):

.. code-block:: yaml

   rsnapshot__hosts:

     - name: '{{ inventory_hostname }}'
       local: True

Include additional filesystems in the local host backup, important when
``one_fs`` option is enabled. All filesystems will be backed up relative to the
``dest_root`` path:

.. code-block:: yaml

   rsnapshot__hosts:

     - name: '{{ inventory_hostname }}'
       filesystems: [ '/home', '/srv', '/var' ]

Alternatively, back up different filesystems into separate subdirectories:

.. code-block:: yaml

   rsnapshot__hosts:

     - name: '{{ inventory_hostname }}'
       filesystems:
         '/':     'rootfs/'
         '/home': 'home/'
         '/srv':  'srv/'
         '/var':  'var/'

Syntax
~~~~~~

Each configuration entry is a string that denotes the inventory name or FQDN of
the host to back up. Alternatively, configuration entries are defined as YAML
dictionaries with specific parameters:

``name``
  Required. Either the name of the host in the Ansible inventory (equivalent of
  ``inventory_hostname``), or a FQDN of the host to back up. Configuration
  entries with the same ``name`` parameter are merged together and can change
  the host configuration conditionally.

  If the configuration entry is specified as a string, for example being based
  on the Ansible ``groups`` variable, the string will be converted to
  a ``name`` parameter. Additional configuration can then be applied using
  configuration entries with the same name.

``fqdn``
  Optional. Specify the Fully Qualified Domain Name of the host to back up. If
  this parameter is specified, it overrides the FQDN detected automatically by
  Ansible facts (if the host is in the Ansible inventory) and disables fact
  gathering for a given host. If you configure an external host to back up and
  specify its FQDN as the ``name`` parameter, you don't need to specify the
  ``fqdn`` parameter.

``local``
  Optional, boolean. If defined and ``True``, the host is considered local and
  SSH configuration will not be applied. The backup paths will be local as
  well. This parameter should not be used, unless you configure backups for the
  backup host itself, usually named as ``'{{ inventory_hostname }}'``.

``state``
  Optional. If not defined or ``present``, the host configuration will be
  created, SSH keys will be deployed to the hosts, and SSH host fingerprints
  will be stored. If ``absent``, the host configuration will be removed, but
  running backup jobs will not be stopped and existing snapshots will not be
  touched. If ``ignore``, a given configuration entry will not be evaluated
  druing role execution. This can be used to conditionally activate
  configuration entries.

``dest_root``
  Optional. The relative destination directory, added to the ``snapshot_root``
  directory path. By default it's set to :file:`./` which means the same
  directory as the ``snapshot_root`` directory.

``filesystems``
  Optional. A string or a YAML list of filesystems which should be backed up by
  :command:`rsnapshot`. This is only relevant if the ``one_fs`` configuration
  option is enabled (by default it is enabled).

  The :file:`/` filesystem is backed up automatically, but with ``one_fs``
  enabled the :command:`rsync` script will not traverse beyond the filesystem
  boundaries. With this parameter, an user can tell :command:`rsnapshot` to
  back up additional filesystems in addition to the :file:`/` filesystem. They
  will be backed up relative to the path specified as the ``dest_root``, by
  default :file:`./`, which should reflect their original placement in the
  source filesystem.

  This parameter can also be defined as a YAML dictionary, with dictionary key
  specifying the source filesystem path, and dictionary value specifying the
  destination path, relative to ``snapshot_root`` directory. This can be used
  to separte different filesystem snapshots into their own subdirectories.

``options``
  Optional. List of the :file:`rsnapshot.conf` configuration options, defined
  in the same format as the :ref:`rsnapshot__ref_configuration` variable. The
  ``options`` parameter is merged between different configuration entries and
  options from different entries can modify each other according to their order
  in the configuration. This can be used to modify the default options for
  a specific host.

``excludes``
  Optional. List of the file patterns to exclude from the backup, stored in the
  :file:`excludes.txt` file in each host configuration directory. The list is
  defined in the same format as the :ref:`rsnapshot__ref_excludes_includes`
  variable. The ``excludes`` parameter is merged between different
  configuration entries and exclude patterns from different entries can modify
  each other according to their order in the configuration. This can be used to
  modify the default list of exclude patterns for a specific host.

``includes``
  Optional. List of the file patterns to include in the backup, stored in the
  :file:`includes.txt` file in each host configuration directory. The list is
  defined in the same format as the :ref:`rsnapshot__ref_excludes_includes`
  variable.  The ``includes`` parameter is merged between different
  configuration entries and include patterns from different entries can modify
  each other according to their order in the configuration. This can be used to
  modify the default list of include patterns for a specific host.

``overrides``
  Optional. String or YAML list of configuration options appended to each
  ``backup`` option in the :file:`rsnapshot.conf` configuration file. Normally
  the role uses the overrides to define what SSH identity to use for a given
  host and what SSH port to connect to; users can specify additional overrides
  using this parameter. These overrides will be added to each ``backup``
  configuration entry generated by the role.

``rsync``
  Optional, boolean. If not specified or ``True``, the role will install APT
  packages specified in the :envvar:`rsnapshot__host_packages` variable (by
  default ``rsync``) on the remote host to back up and set up the
  :command:`/usr/local/bin/rrsync` wrapper script. If these tasks cannot or
  shouldn't be performed on the remote host, you can disable them by seeting
  this parameter to ``False``.

``rrsync_source``
  Optional. Absolute path on the host to back up to the :command:`rrsync`
  wrapper script source (by default
  :file:`/usr/share/doc/rsync/scripts/rrsync`). The role will copy the script
  to the :file:`/usr/local/bin/` directory and make it executable. The role
  will automatically detect any tarballs with the ``.gz`` extension and extract
  their contents; the ``.gz`` extenion should not be included in the path
  specified in this parameter.

``rrsync_binary``
  Optional. Absolute path on the host to back up where the :command:`rrsync`
  wrapper script should be installed (by default
  :file:`/usr/local/bin/rrsync`).

``ssh_key``
  Optional, boolean. If not specified or ``True``, the role will install the
  specified or default SSH public key on the host to back up, so that
  :command:`rsnapshot` can connect to it over SSH.

``ssh_scan``
  Optional, boolean. If not specified or ``True``, the role will scan the SSH
  fingerprint of the host to back up, so that :command:`rsnapshot` command can
  connect to it unattended. If the SSH public key has been added or modified on
  the host to back up, the role will remove the previously saved SSH
  fingerprints assuming that the host has been reinstalled and new SSH host
  keys are present.

``ssh_user``
  Optional. The name of the user to which the :command:`rsnapshot` command will
  connect over SSH and on which the SSH public key will be installed. By
  default ``root``. Use of an unprivileged account is not implemented at the
  moment.

``ssh_port``
  Optional. The TCP port of the SSH service the :command:`rsnapshot` should use
  to connect to the host which is being backed up.

``ssh_identity``
  Optional. A name of the SSH identity to use for a given host. If not
  specified, the identity defined in :envvar:`rsnapshot__ssh_main_identity`
  will be used by default. The available SSH identities can be listed by
  executing the :file:`/etc/ansible/facts.d/rsnapshot.fact` script on the
  :command:`rsnapshot` host.

``ssh_options``
  Optional. A string with SSH options added with the SSH key in the
  :file:`~/.ssh/authorized_keys` file on the host to back up. If not specified,
  the value of the :envvar:`rsnapshot__ssh_options` variable will be used by
  default.

``ssh_command``
  Optional. The command to execute on the host to back up, defined with the SSH
  key in the :file:`~/.ssh/authorized_keys` file. If not specified, the value
  of the :envvar:`rsnapshot__ssh_command` variable will be used by default.


.. _rsnapshot__ref_excludes_includes:

rsnapshot__excludes, rsnapshot__includes
----------------------------------------

The ``rsnapshot__*_excludes`` and ``rsnapshot__*_includes`` variables define
the default lists of file patterns to exclude and included in the snapshots. By
default the snapshots are designed to include everything, but exclude specific
paths in the filesystem; this way any paths not specified explicitly in the
configuration should be backed up automatically.

The default lists of exclude and include patterns are combined with the
``item.excludes`` and ``item.includes`` parameters of the host configuration
entries in the :ref:`rsnapshot__ref_hosts` variables. They can be used to
modify existing file patterns or add new ones.

See the :man:`rsync(1)` manual page, "INCLUDE/EXCLUDE PATTERN RULES" section
for more information about file patterns.

Examples
~~~~~~~~

See the :envvar:`rsnapshot__default_excludes` variable for the list of the file
patterns that are defined by default.

Define a list of file patterns to exclude from backups:

.. code-block:: yaml

   rsnapshot__excludes:

     - '/no-backup'
     - '/scratch'

Include eveyrthing in the backup, barring any excluded files:

.. code-block:: yaml

   rsnapshot__includes:

     - '/*'

Syntax
~~~~~~

Each entry in the list can be a string that defines a file pattern. The default
behaviour is dependent on the variable type - files will be excluded by default
if defined in the ``rsnapshot__*_excludes`` variables, and included if they are
defined in the ``rsnapshot__*_includes`` variables.

Alternatively, you can define each file pattern using the YAML dictionary
syntax with specific parameters:

``name``
  Required. The file pattern to exclude/include in the backups. The entries
  with the same ``name`` parameter are merged together, this can be used to
  modify previously defined file patterns conditionally.

``state``
  Optional. If not specified or ``present``, a given file pattern will be
  present in the generated :file:`excludes.txt`` or :file:`includes.txt`
  configuration files. If ``absent``, the pattern will not be present in the
  configuration files. If ``ignore``, a given configuration entry will not be
  evaluated by the role during execution.

``rule``
  Optional. Specify the rule type to use for a given file pattern (see
  :man:`rsync(1)` for detailed explanation). Possible values are: ``exclude``,
  ``include``, ``merge``, ``dir-merge``, ``hide``, ``show``, ``protect``,
  ``risk``, ``clear``. This can be used to override the default file pattern
  type, to include a pattern in the :file:`excludes.txt` file, or exclude in
  the :file:`includes.txt` file.


.. _rsnapshot__ref_configuration:

rsnapshot__configuration
------------------------

The ``rsnapshot__*_configuration`` variables define the default options
included in the generated :file:`rsnapshot.conf` configuration files. The
defaults are merged with the ``item.options`` parameter in each host
configuration entry, which can be used to override specific configuration
options on a host-by-host basis.

The information about possible options and their meaning can be found in the
:man:`rsnapshot(1)` manpage.

Examples
~~~~~~~~

See the :envvar:`rsnapshot__original_configuration` to see the original values
of the configuration options.

The :envvar:`rsnapshot__default_configuration` contains all of the values
modified by the role by default.

Syntax
~~~~~~

The options can be specified as a list of YAML dictionaries, each dictionary
key being the option name, and the dictionary value being the option value (you
should specify only one key/value pair this way per the list element).

Alternatively, if the YAML dictionary key ``name`` is present, the role will
interpret a given entry using specific parameters:

``name``
  Required. The name of the configuration option. Entries with the same
  ``name`` parameter are merged together, this can be used to modify the
  configuration options conditionally.

``option``
  Optional. Specify an alternative name of the configuration option. This is
  used when a given option can be present more than once in the configuration
  file, for example ``retain``. In that case, the option value will be taken
  from the ``name`` parameter and additional arguments will be taken from the
  ``value`` parameter.

``value``
  The value of a given configuration option, usually a string or a number. The
  role does not interpret booleans, lists or dictionaries in any special way.
  Some of the specific configuration options might have their default values
  modified in the configuration file template to support multi-host backups.

``raw``
  Optional. A string or a YAML text block that will be included in the
  configuration file as-is instead of the ``name``/``value`` parameters. This
  can be used for parts of the configuration that are too complex to implement
  them using other parameters. Remember that the :file:`rsnapshot.conf`
  configuration file uses tab characters as separators between option name,
  value and other arguments.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated config file. If ``absent``, the option will be
  removed from the generated configuration file. If ``ignore``, the entry will
  not be evaluated during role execution. If ``comment``, a given configuration
  option will be includedd, but it will be commented out.

``comment``
  Optional. String or YAML text block with comments for a given configuration
  option.

``section``
  Optional. Name of the section in which to include a given configuration
  option. Possible sections are defined in the
  :envvar:`rsnapshot__configuration_sections` variable. If a section is not
  specified, an ``unknown`` section will be used by default.

``weight``
  Optional. A positive or negative number which modifies the "weight" of
  a given configuration option. The weight affects the order of configuration
  options in a given section; use negative number to move a given option higher
  in the file, and positive number to move it lower in the file.
