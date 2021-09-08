.. Copyright (C) 2015-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

iPXE integration
----------------

The :ref:`debops.preseed` role integrates very well with the Debian-Installer
configuration provided with the :ref:`debops.ipxe` role. You can use the menu
system defined there to select different Preseed flavors and provide needed
parameters like hostname and Debian mirror to use.


How Debian Installer preseeding works
-------------------------------------

The Debian Installer can use automatic :file:`preseed.cfg` lookup system when
specific kernel parameters are defined during the boot process. These
parameters are:

.. code-block:: none

   auto=true url=<seed>

If a simple string and not a full URL is specified as ``<seed>``, Debian
Installer will expand it to:

.. code-block:: none

   http://<seed>/d-i/<release>/preseed.cfg

To enable Preseeded installation, after starting the Debian Installer, navigate
the menu to "Advanced options" -> "Automated Install". Next, press the
``<Tab>`` key, this will let you enter additional boot options. Now you can
specify the URL of the Preseed file. The menu system implemented in the
:ref:`debops.ipxe` role can do this automatically for you when you selet
preseed installation method.


Default set of Preseed flavors
------------------------------

Debian Preseeding can be used to provision various types of hardware or virtual
machines. Not all of them are the same however, and to facilitate that, the
:ref:`debops.preseed` role implements a system of preseed "flavors" which can
be selected to enable different configuration options. The current set of
"flavors" available by default is:

+---------------------------------------------------+---------------+---------------------+
|                                                   | root-only     | administrative user |
+---------------------------------------------------+---------------+---------------------+
| hardware, non-free APT repos, manual partitioning | ``debian``    | ``debian-user``     |
+---------------------------------------------------+---------------+---------------------+
| virtual machine, guided single LVM parition       | ``debian-vm`` | ``debian-vm-user``  |
+---------------------------------------------------+---------------+---------------------+

If we assume that the DNS domain of the cluster is ``example.org``, the Preseed
flavors are presented as DNS subdomains of the main server domain by default
defined as ``seed.example.org``. For this to work reliably, DNS database needs
to contain CNAME records that point to the Preseed server, for example:

- ``debian.seed.example.org``
- ``debian-vm.seed.example.org``
- ``debian-user.seed.example.org``
- ``debian-vm-user.seed.example.org``

For convenience, you might also want to create a short DNS records for the
``*.seed`` "domain" that can be used in the menu system implemented by
the :ref:`debops.ipxe` role:

- ``debian.seed``
- ``debian-vm.seed``
- ``debian-user.seed``
- ``debian-vm-user.seed``

You can create your own Preseed "flavors" in the same way, just remember to add
the needed CNAME DNS records.


Example inventory
-----------------

To configure the Preseed server, you can add a host to the
``[debops_service_preseed]`` group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_preseed]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.preseed`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/preseed.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::preseed``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the :ref:`debops.preseed` Ansible
role:

- `"Hands-Off" Debian Installation`__

  .. __: https://hands.com/d-i/

- The `Debian Installer Pressed page`__ on Debian Wiki

  .. __: https://wiki.debian.org/DebianInstaller/Preseed
