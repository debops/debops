.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variables: configuration
================================

some of ``debops.netboot_assistant`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _netboot_assistant__ref_installs:

netboot_assistant__installs
---------------------------

The ``netboot_assistant__*_installs`` variables define a list of Debian or
Ubuntu netboot images maintained by the D-I Netboot Assistant service. The
variables are filtered using the :ref:`universal_configuration` system.

The install definitions correspond to the list of known repositories defined in
the :file:`/etc/di-netboot-assistant/di-sources.list` configuration file,
included in the ``di-netboot-assistant`` Debian package.

Examples
~~~~~~~~

See the :envvar:`netboot_assistant__default_installs` variable for a list of
the default Debian netinst install definitions.

Syntax
~~~~~~

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. An identifier for a particular configuration entry, not used
  otherwise. Configuration entries with the same ``name`` parameter are merged
  together, this can be used to modify entries from the role defaults using
  Ansible inventory.

``image``
  Required unless ``raw`` is used. Name of the OS release a given entry
  defines. The OS releases which will be installed should be one of the
  releases specified in the :file:`di-sources.list` configuration file. Users
  can also get a list of available releases by running the
  :command:`di-netboot-assistant install` command.

``arch``
  Required unless ``raw`` is used. Name of the OS architecture a given entry
  defines. The OS architectures which will be installer should be one of the
  architectures specified in the :file:`di-sources.list` configuration file..

``state``
  Optional. If not specified or ``present``, a given Debian Installer
  release/architecture combination will be downloaded and installed in the TFTP
  directory. If ``absent``, a given release/architecture combination will be
  removed from the TFTP directory. If ``ignore``, a given configuration entry
  will not be evaluated by the role. This can be used to modify the
  configuration conditionally.

``firmware``
  Optional, boolean. If defined and ``True``, the role will make sure that the
  non-free firmware is included in the specified installer. If not defined or
  ``False``, the non-free firmware state will not be changed.

Alternatively, raw :command:`di-netboot-assistant` subcommands and options can
be specified using the parameters below:

``raw``
  Optional. Specify a :command:`di-netboot-assistant` subcommand with options
  and arguments. This command will be executed on each run of the role with the
  "changed" status.

``creates``
  Optional. Specify an absolute path to a file on the remote host; the role
  will not execute the specific subcommand if a given file exists.

``removes``
  Optional. Specify an absolute path to a file on the remote host; the role
  will not execute the specific subcommand if a given file does not exist.


.. _netboot_assistant__ref_configuration:

netboot_assistant__configuration
--------------------------------

The ``netboot_assistant__*_configuration`` variables define the contents of the
:file:`/etc/di-netboot-assistant/di-netboot-assistant.conf` configuration file.
The variables are combined in order defined in the
:envvar:`netboot_assistant__combined_configuration` variable and can affect
each other. Configuration uses the :ref:`universal_configuration` system to
parse the YAML entries an generate a the final contents of the configuration
file.

Examples
~~~~~~~~

See the :envvar:`netboot_assistant__original_configuration` variable for the
contents of the original configuration file defined in YAML.
The :envvar:`netboot_assistant__default_configuration` variable contains the
options modified by the role.

Syntax
~~~~~~

Each configuration entry defines one configuration option. The configuration is
specified as a YAML dictionary with specific parameters:

``name``
  Required. The name of the configuration option. Multiple entries with the
  same ``name`` parameter are merged together in order of appearance and can
  affect each other.

``value``
  The value of a given configuration option.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated config file. If ``absent``, a given
  configuration option will not be included in the file. If ``comment``, the
  option will be included, but commented out. If ``ignore``, a given
  configuration entry will not be processed during role execution.

``comment``
  Optional. A comment about a given configuration option.

``single_quotes``
  Optional, boolean. Most of the values in the default configuration file are
  quoted using double quotes (``""``), but to allow the "passthrough" of
  environment variable names without expanding them, the value needs to be
  quoted using single quotes (``''``). When this parameter is defined and True,
  the template will use single quotes for a given value.
