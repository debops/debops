Default variables: configuration
================================

some of ``debops.ipxe`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _ipxe__ref_debian_netboot_release_map:

ipxe__debian_netboot_release_map
--------------------------------

The ``ipxe__debian_netboot_*_release_map`` variables define a list of Debian
Installer releases known to the role. These releases will be downloaded and
prepared by the :ref:`debops.ipxe` Ansible role for use on the local network.

The Debian netboot installers are prepared in an elaborate directory structure
inside of the :envvar:`ipxe__debian_netboot_pxe_root` directory, which supports
multiple OS releases, architectures and installation flavors. Each installer
optionally can be supplemented by a set of non-free firmware packages provided
by Debian to allow use of hardware that requires it.

Examples
~~~~~~~~

See the :envvar:`ipxe__debian_netboot_default_release_map` variable for an
example configuration.

Syntax
~~~~~~

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. An identifier for a particular configuration entry, not used
  otherwise. Configuration entries with the same ``name`` parameter are merged
  together, this can be used to modify entries from the role defaults using
  Ansible inventory.

``state``
  Optional. If not specified or ``present``, a given Debian Installer release
  will be downloaded and prepared by the role. If ``absent``, a given release
  will be skipped; existing configuration will not be modified or removed.
  If ``ignore``, a given configuration entry will not be evaluated by the role.
  This can be used to modify the configuration conditionally.

``release``
  Required. Name of the OS release a given entry defines. The OS releases which
  will be prepared are filtered by the :envvar:`ipxe__debian_netboot_releases`
  list variable.

``architecture``
  Required. Name of the OS architecture a given entry defines. The OS
  architectures which will be prepared are filtered by the
  :envvar:`ipxe__debian_netboot_architectures` list variable.

``netboot_url``
  Optional. An URL to the :file:`netboot.tar.gz` tarball which contains the
  installer files. If not specified, the URL will be generated automatically
  based on the selected Debian mirror, release and architecture.

``netboot_subdir``
  Optional. Normally empty, this parameter can be used to specify
  a subdirectory in the installer directory which will be included in the URL
  to the installer tarball. Currently this is only useful to define
  a "gtk-based" installer entry which provides the graphical installer. At the
  moment the only sensible value is ``/gtk``.

``netboot_version``
  Required. Specify the version of the installer to download and prepare. This
  parameter will be changed over time as the new installer version are
  released; the :file:`current` symlink will be updated to match the selected
  version. The current and upstream versions can be checked in the DebOps
  monorepo root directory by running the :command:`make versions` command.

``netboot_checksum``
  Optional. Specify the checksum of the installer tarball, usually a SHA256. If
  not specified, the file checksum will not be verified. The checksum should be
  updated on any version changes to match the new tarball.

``netboot_current``
  Optional, boolean. If not specified or ``True``, the role will update the
  :file:`current` symlink to the specified installer version. If ``False``,
  existing symlink will not be updated.

``firmware_url``
  Optional. An URL to the :file:`firmware.cpio.gz` file which contains the
  firmware packages. If not specified and the ``firmware_version`` parameter is
  specified, the URL will be generated automatically based on the firmware
  mirror URL, OS release and firmware version.

``firmware_version``
  Optional. Specify the version of the firmware file to download and add to the
  Debian installer :file:`initrd.gz` file. If not specified, the firmware will
  not be downloaded.

``firmware_checksum``
  Optional. Specify the checksum of the firmware file, usually a SHA256. If not
  specified, the file checksum will not be verified. The checksum should be
  updated on any firmware version changes to match the new file.


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
       echo Error occured, press any key to return to menu...
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
    a given iPXE variable.

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
