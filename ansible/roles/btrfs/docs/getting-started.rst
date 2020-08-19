Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst


Example inventory
-----------------

To manage Btrfs on host given in ``debops_service_btrfs`` Ansible inventory
group:

.. code:: ini

    [debops_service_btrfs]
    hostname

Example playbook
----------------

Here's an example playbook that can be used to manage Btrfs:

.. literalinclude:: playbooks/btrfs.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`docs/playbooks/btrfs.yml` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider
using the `DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::btrfs``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::btrfs:pkts``
  Tasks related to the installation of required packages.

``role::btrfs:subvolumes``
  Tasks related to managing Btrfs subvolumes.
