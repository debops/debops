.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Replacing ``ifupdown`` scripts with ``systemd-networkd``
--------------------------------------------------------

The default non-GUI Debian installation uses the ``ifupdown`` package to
configure network interfaces. It's not compatible with the
:command:`systemd-networkd` service, therefore it's best to purge it from the
host after the new configuration has been applied. This has to be done through
local console, since during removal the post-rm scripts will bring the network
interfaces down, disconnecting the host from the network.

Specific steps to take to replace the ``ifupdown`` package with
:command:`systemd-networkd` service:

1. Make sure that the host is in the ``[debops_service_networkd]`` Ansible inventory group.

   .. code-block:: none

      [debops_all_hosts]
      hostname

      [debops_service_networkd]
      hostname

2. Apply the :ref:`debops.networkd` playbook, check if the host has network connection.

   .. code-block:: console

      user@host:~$ debops check service/networkd -l hostname
      user@host:~$ debops run service/networkd -l hostname

3. Login to the host on the local console, purge ``ifupdown`` package and reboot the host.

   .. code-block:: console

      user@host:~$ sudo apt purge ifupdown
      user@host:~$ sudo systemctl reboot

4. Login to the host and check if the new configuration has been set up
   correctly. Apply the :ref:`debops.resolved` playbook to configure
   :file:`/etc/resolv.conf` configuration file.

   .. code-block:: console

      user@host:~$ debops check service/resolved -l hostname
      user@host:~$ debops run service/resolved -l hostname


Example inventory
-----------------

To manage the network configuration using :command:`systemd-networkd` service,
the host needs to be included in the ``[debops_service_networkd]`` Ansible
inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_networkd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.networkd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/networkd.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::networkd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
