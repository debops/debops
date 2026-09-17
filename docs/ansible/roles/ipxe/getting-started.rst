.. Copyright (C) 2015-2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Debian netboot installer support
--------------------------------

The :ref:`debops.netboot_assistant` role provides support for installation of
local Debian or Ubuntu netinst images, which can be used via the iPXE boot menu
to launch Debian Installer over the network. See its documentation for details.


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
   :lines: 1,5-


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

- `netboot.xyz`__ - public network boot server, available from DebOps Boot Menu

  .. __: https://netboot.xyz/

- `SAL's Boot Menu`__ - another public network boot server available via DebOps Boot Menu

  .. __: http://boot.salstar.sk/

- `Rackspace Boot Server`__, available via DebOps Boot Menu

  .. __: http://boot.rackspace.com/
