.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

To install and configure ``keepalived`` on a given host, it should be included in
a specific Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname   ansible_host=hostname.example.org

   [debops_service_keepalived]
   hostname

Of course, installing :command:`keepalived` on a single host does not provide
any benefits, so it's better to create a cluster instead:

.. code-block:: none

   [debops_all_hosts]
   node1   ansible_host=node1.example.org
   node2   ansible_host=node2.example.org
   node3   ansible_host=node3.example.org

   [debops_service_keepalived]
   node1
   node2
   node3

You can also create multiple separate :command:`keepalived` clusters in
a single Ansible inventory by using separate host groups. Each host group can
have its own configuration:

.. code-block:: none

   [debops_all_hosts]
   node1   ansible_host=node1.example.org
   node2   ansible_host=node2.example.org
   node3   ansible_host=node3.example.org
   node4   ansible_host=node4.example.org

   [cluster_group_one]
   node1
   node2

   [cluster_group_two]
   node3
   node4

   [debops_service_keepalived:children]
   cluster_group_one
   cluster_group_two

Check the :ref:`keepalived__example_floating_ip` documentation section to see
how the role can be configured to utilize separate inventory groups.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.keepalived`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/keepalived.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::keepalived``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.keepalived`` Ansible role:

- Manual pages: :man:`keepalived(8)`, :man:`keepalived.conf(5)`

- Lots of configuration examples can be found in the
  :file:`/usr/share/doc/keepalived/samples/` directory, provided with the
  ``keepalived`` APT package.

- Example of `floating IP address configuration with keepalived`__. Based on
  CentOS, however the service configuration is the same on different operating
  systems.

  .. __: https://www.centlinux.com/2018/08/keepalived-configure-floating-ip-centos-7.html

- Example of `extending keepalived functionality through scripts`__.

  .. __: https://tobru.ch/keepalived-check-and-notify-scripts/
