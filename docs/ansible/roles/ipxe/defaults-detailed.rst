.. Copyright (C) 2015-2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variables: configuration
================================

some of ``debops.ipxe`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _ipxe__ref_scripts:

ipxe__scripts
-------------

The ``ipxe__*_scripts`` variables define a list of iPXE scripts stored in the
:envvar:`ipxe__tftp_root` directory (by default :file:`/srv/tftp/`). At boot
time, the iPXE boot loader will download and execute the :file:`menu.ipxe`
script (this is just a convention controlled by the DHCP server). The script
contains iPXE commands which can be used to define an interactive menu,
chainload other scripts and boot operating systems.

Examples
~~~~~~~~

See the :envvar:`ipxe__default_scripts` variable for an example configuration.

Modify an existing default configuration to include additional main menu items
that boot an ISO image over HTTP. When the new option is selected, the iPXE
boot loader will load the new :file:`iso-image.ipxe` script:

.. code-block:: yaml

   - name: 'menu.ipxe'
     options:

       - name: 'main-menu'
         raw: |
           item --key d debian-installer ${space} Install Debian GNU/Linux on this host [d]
           item iso-image ${space} Boot custom ISO image
           item

   - name: 'iso-image.ipxe'
     raw: |
       set iso-root http://boot.{{ ansible_domain }}/iso/
       set iso-img custom-image.iso

       initrd ${iso-root}/${iso-img}
       chain memdisk iso || goto error

       :error
       echo Error occurred, press any key to return to menu...
       prompt
       set menu main_menu
       chain menu.ipxe
     state: 'present'

Syntax
~~~~~~

Each configuration entry defines one iPXE script. The configuration is
specified as a YAML dictionary with specific parameters:

``name``
  Required. Name of the iPXE script. You can include subdirectories in the name
  (for example ``extra/menu.ipxe`` which will be created automatically.
  Entries with the same ``name`` parameter are merged together, this can be
  used to modify existing entries as needed.

``comment``
  Optional. A string or a YAML text block with a comment added at the top of
  the iPXE script.

``state``
  Optional. If not defined or ``present``, a given iPXE script will be created
  by the role. If ``absent``, the specified iPXE script will be removed by the
  role. If ``ignore``, a given configuration entry will be ignored by the role
  during its execution. This can be used to activate configuration entries
  conditionally.

``raw``
  Optional. A YAML text block that contains the iPXE script, added as-is in the
  generated file. The ``#!ipxe`` shebang will be added automatically at the top
  of the file and does not have to be specified. See the `iPXE documentation`__
  for more details about scripting the bootloader.

  .. __: https://ipxe.org/scripting

``options``
  Optional. An alternative way to define the contents of the generated iPXE
  script. The ``options`` parameters from different configuration entries are
  merged together and elements of the options list can affect each other. This
  is a list of YAML dictionaries, each dictionary describes a part of the
  generated file using specific parameters:

  ``name``
    Required. An identifier of a given part of the iPXE script. If ``raw``
    parameter is specified, the ``name`` parameter is not used otherwise. If
    ``raw`` parameter is not specified, the ``name`` parameter is the second
    element in the script line (see ``value`` and ``command`` parameters). By
    default this defines an iPXE variable name. Option list entries with the
    same ``name`` parameter are merged together.

  ``value``
    Optional. If ``raw`` parameter is not specified, this parameter defines the
    third element of the script line. By default this defines a value of
    a given iPXE variable. You can specify a string or a list which will be
    concatenated with spaces as separators.

  ``command``
    Optional. If ``raw`` parameter is not specified, this parameter defines the
    first element of the script line, by default ``set`` which defines an iPXE
    variable.

  ``raw``
    Optional. YAML text block that contains a section of the iPXE script.

  ``comment``
    Optional. A string or YAML text block with a comment about a given script
    section.

  ``state``
    Optional. If not specified or ``present``, a given script section will be
    included in the generated file. If ``absent``, a given script section will
    be removed from the generated file.
