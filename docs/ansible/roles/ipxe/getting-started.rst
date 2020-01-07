Getting started
===============

.. contents::
   :local:


Debian netboot installer support
--------------------------------

By default the role will download and prepare a set of Debian netboot
installers for various OS releases. The Debian installers will be available via
the boot menu, with a possibility to boot into the text, graphical or expert
install. A preseeded configuration is also available for larger environments.

Optionally, the role can include the non-free firmware required by certain
devices (for example network cards) for convenience.The installation of the
non-free firmware is disabled by default, you can enable it using the
:envvar:`ipxe__debian_netboot_firmware` variable. The firmware will also be
enabled automatically if non-free repositories are configured on the host in
APT.


Additional services required
----------------------------

The ``debops.ipxe`` role relies on other DebOps roles to provide the needed
DHCP and TFTP services. You can use either :ref:`debops.dnsmasq` on an internal
network to configure DHCP, DNS, PXE and TFTP services, or use
:ref:`debops.dhcpd` and :ref:`debops.tftpd` roles to set up a more
comprehensive network environment.


Example inventory
-----------------

To configure iPXE boot firmware on a given host, you need to include in the
``[debops_service_ipxe]`` Ansible inventory group:

.. code-block:: none

   [debops_service_ipxe]
   hostname

If you are using :ref:`debops.dnsmasq` to provide DHCP and TFTP services, you
can configure iPXE environment on the same host. Alternatively,
:ref:`debops.tftpd` role can be used to provide TFTP service on a separate host
on the network, which is then specified via DHCP as the "next server" for other
hosts to boot from.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.ipxe`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ipxe.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::ipxe``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.ipxe`` Ansible role:

- `iPXE scripting documentation`__, `command reference`__

  .. __: https://ipxe.org/scripting
  .. __: https://ipxe.org/cmd

- `Installing Debian using network booting`__

  .. __: https://wiki.debian.org/PXEBootInstall

- `Non-free firmware in Debian`__ documentation page

  .. __: https://wiki.debian.org/Firmware

- `How to include non-free firmware in Debian netboot installer`__

  .. __: https://wiki.debian.org/DebianInstaller/NetbootFirmware

- `netboot.xyz`__ - public network boot server, available from DebOps Boot Menu

  .. __: https://netboot.xyz/

- `SAL's Boot Menu`__ - another public network boot server available via DebOps Boot Menu

  .. __: http://boot.salstar.sk/

- `Rackspace Boot Server`__, available via DebOps Boot Menu

  .. __: http://boot.rackspace.com/
