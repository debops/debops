.. Copyright (C) 2014-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

By default ``debops.dhcpd`` installs the ISC DHCP server with some default
configuration. The server will not be authoritative, and will have a default
subnet configuration taken from ``ansible_default_ipv4`` and
``ansible_default_ipv6``. Dynamic lease assignment will not work until you
configure subnets with valid address ranges.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.dhcpd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/dhcpd.yml
   :language: yaml
   :lines: 1,6-
