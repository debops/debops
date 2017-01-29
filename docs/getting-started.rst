Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To configure volume snapshots on host given in
``debops_service_snapshot_snapper`` Ansible inventory group:

.. code:: ini

    [debops_service_snapshot_snapper]
    hostname

Example playbook
----------------

Here's an example playbook that uses the ``debops-contrib.snapshot_snapper`` role:

.. literalinclude:: playbooks/snapshot_snapper.yml
   :language: yaml

The playbooks is shipped with this role under
:file:`./docs/playbooks/snapshot_snapper.yml` from which you can symlink it to your
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

``role::snapshot_snapper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::snapshot_snapper:reinit``
  Execute tasks related to automatic reinitialization of volume snapshots.
