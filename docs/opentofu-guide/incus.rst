.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _tofu_incus:

A container fleet with OpenTofu and Incus
=========================================

.. contents::
   :local:

This recipe shows the whole loop. OpenTofu creates a fleet of Incus
containers, the inventory bridge renders them into the Ansible
inventory, and DebOps configures them. One view, one controller, a
fleet you can rebuild from a plan file.

Name the containers after the services they will run. The site
network's auto-created DNS records register the instance names as
hostnames: a container named ``gitlab`` answers on
``gitlab.example.org`` without extra work.


The view
--------

Create the view with the provider pinned:

.. code-block:: console

   alice@controller:~$ debops tofu mkview fleet -p lxc/incus

The provider talks to the local Incus daemon through its Unix socket
by default. For a remote Incus host, configure the provider in the
view's :file:`main.tf` and reach the containers through that host. The containers on a bridge
network are often reachable only through it, which matters for the
inventory below.

Declare the fleet as one ``for_each`` map, with the per-instance
attributes alongside:

.. code-block:: text

   # tofu/views/<view>/main.tf
   variable "containers" {
     type = map(object({
       address = optional(string)
       groups  = optional(list(string), [])
     }))
     default = {
       "web-1"  = { groups = ["web"] }
       "web-2"  = { groups = ["web"] }
       "gitlab" = {}
     }
   }

   resource "incus_instance" "fleet" {
     for_each = var.containers

     name      = each.key
     image     = "images:debian/13/cloud"
     type      = "container"
     profiles  = ["default"]

     lifecycle {
       ignore_changes = [device]
     }
   }

The exact resource shape depends on your network setup. Containers
with a static address need a ``device`` entry for the NIC. Containers
on DHCP do not. The ``ignore_changes`` above keeps OpenTofu from
fighting the addresses the DHCP server hands out.


The seed output
---------------

The bridge reads the ``inventory_seed`` output. Compose it from the
instances:

.. code-block:: text

   # tofu/views/<view>/main.tf
   output "inventory_seed" {
     value = {
       for name, instance in incus_instance.fleet : name => {
         address = instance.ipv4_address
         status  = instance.status
         jump    = "incus.example.org"
         groups  = var.containers[name].groups
       }
     }
   }

The ``jump`` attribute puts the Incus host between Ansible and the
containers: the rendered host lines carry
``ansible_ssh_common_args='-o ProxyJump=incus.example.org'``, and the
bridge network stays off the wire.

Plan and apply:

.. code-block:: console

   alice@controller:~$ debops tofu -V fleet update
   alice@controller:~$ debops tofu -V fleet plan
   alice@controller:~$ debops tofu -V fleet plans apply 1


The inventory render
--------------------

.. code-block:: console

   alice@controller:~$ debops tofu -V fleet inventory
   alice@controller:~$ debops run site -l web-1

The render writes the hosts file of the ``fleet`` Ansible view and
the variables files beside it. From here the fleet is an ordinary DebOps inventory. The service
playbooks target their ``debops_service_*`` groups, and the role
wiring lives in your own :file:`group_vars/` and :file:`host_vars/`
files beside the rendered ones.

The container addresses come from DHCP. If OpenTofu wrote the state before the leases settled, the rendered
inventory carries empty addresses. The bridge skips those hosts with
a notice. Run :command:`debops tofu -V fleet inventory --force` after
a refresh-only apply, or enable ``tofu.inventory.state_refresh``.


Caveats
--------

**The provider caps every wait at three minutes.** Containers that
wait for a DHCP lease can outlive the wait. The fleet pattern that
works: create the containers without waiting for the addresses, then
pull the leases with a refresh-only apply:

.. code-block:: console

   alice@controller:~$ debops tofu -V fleet apply -refresh-only

**Dual-homed containers need explicit network config.** The
cloud-init fallback of the Debian cloud images configures only the
first NIC. The second comes up link-up with no address. Write an
explicit version-2 ``user.network-config`` for both interfaces. The
user-data and network-config land only at creation, so changing them
means recreating the container.

**Recreated containers are new hosts.** A recreation gets a new DHCP
lease and new host keys. The bridge re-renders the inventory, and
Ansible's ``accept-new`` re-records the key into the project's
known-hosts store. Your own ``~/.ssh/known_hosts`` still holds the
old key. Run :command:`ssh-keygen -R` on it or expect the refusal.

**Statuses gate the render.** Stopped containers carry a ``Stopped``
status, and the bridge skips statuses it has no instruction for.
Key the behaviour in ``tofu.inventory.host_status``: include
``running``, and decide what a stopped container should do.

**The PKI runs on the controller.** The debops.pki role generates the
root and domain CAs into the project's secret store. The wildcard
certificate covers every service name of the fleet. Deploying
nginx-like services before the PKI exists works. The services gain
their TLS listeners on a re-run once the PKI facts land.


See also
--------

- :ref:`debops_tofu_inventory` for the bridge contract the seed
  output follows
- :ref:`tofu_remote_state` for keeping the fleet state outside the
  controller
- The Incus documentation for the provider resource reference
