Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The default configuration implemented by ``debops.tcpwrappers`` is focused
around whitelisting specific IP addresses, CIDR subnets or other entries. Role
will automatically block all incoming connections using ``/etc/hosts.deny`` and
allow you to specify whitelisted exceptions in ``/etc/hosts.allow``.

To support idempotent configuration of different services, role uses the
Ansible ``assemble`` module to generate the ``/etc/hosts.allow`` file from
fragments located in ``/etc/hosts.allow.d/`` directory. Any changes in the
``/etc/hosts.allow`` file directly will be lost.

Due to SSH service being crucial for Ansible operation, the role takes care not
to block the Ansible Controller host from accessing it using data gathered
automatically by ``debops.core`` role, or by a separate list of Ansible
Controller hosts.

Example inventory
-----------------

The ``debops.tcpwrappers`` role is included by default in the ``common.yml``
DebOps playbook. You don't need to configure anything in the inventory to
enable it.

Example playbook
----------------

``debops.tcpwrappers`` is designed to be used from a playbook or a role as role
dependency. Here's an example configuration:

.. literalinclude:: ../../../../ansible/playbooks/service/tcpwrappers.yml
   :language: yaml
