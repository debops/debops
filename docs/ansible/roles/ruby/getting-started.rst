.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

Example inventory
-----------------

To configure a Ruby environment on a given host or set of hosts, they need to
be added to ``[debops_service_ruby]`` Ansible group in the inventory::

    [debops_service_ruby]
    hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.ruby`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ruby.yml
   :language: yaml
   :lines: 1,5-

