.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

The ``debops.lldpd`` role is included by default in the :file:`common.yml`
DebOps playbook; you don't need to do anything to have it executed.

If you don’t want to let ``debops.lldpd`` role install and configure the
service, you can disable it with the following setting in your inventory:

.. code-block:: yaml

   lldpd__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.lldpd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/lldpd.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::lldpd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.lldpd`` Ansible role:

- Manual pages: :man:`lldpd(8)`, :man:`lldpcli(8)`

- The `lldpd homepage`__

  .. __: https://lldpd.github.io/

- `Link-Layer Discovery Protocol`__ page on Wikipedia

  .. __: https://en.wikipedia.org/wiki/Link_Layer_Discovery_Protocol

- The `community.general.lldp`__ Ansible module which can gather LLDP
  information from hosts.

  .. __: https://docs.ansible.com/ansible/latest/collections/community/general/lldp_module.html
