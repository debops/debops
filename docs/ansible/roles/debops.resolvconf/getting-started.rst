Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.resolvconf`` role is included by default in the ``common.yml``
DebOps playbook; you don't need to add hosts to any Ansible groups to enable
it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.resolvconf`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/resolvconf.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::resolvconf``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.resolvconf`` Ansible role:

- Manual pages: :man:`resolvconf(8)`, :man:`resolv.conf(5)`

- The `resolv.conf`__ Debian Wiki page

  .. __: https://wiki.debian.org/resolv.conf

- Local DNS resolvers available in DebOps: :ref:`debops.dnsmasq`,
  :ref:`debops.unbound`
