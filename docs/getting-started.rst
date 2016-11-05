Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To manage and configure FUSE on a given host it should be included in the
``debops_service_fuse`` Ansible inventory group:

.. code:: ini

   [debops_service_fuse]
   hostname

Example playbook
----------------

Here's an example playbook that uses the ``debops-contrib.fuse`` role:

.. literalinclude:: playbooks/fuse.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`./docs/playbooks/fuse.yml` from which you can symlink it to your
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

``role::fuse``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
