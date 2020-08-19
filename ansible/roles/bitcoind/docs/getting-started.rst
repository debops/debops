.. _bitcoind__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To manage bitcoind on a given host or set of hosts, they need to
be added to the ``[debops_service_bitcoind]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_bitcoind]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops-contrib.bitcoind`` role:

.. literalinclude:: playbooks/bitcoind.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/bitcoind.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::bitcoind``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::bitcoind:pkgs``
  Tasks related to system package management like installing or
  removing packages.
