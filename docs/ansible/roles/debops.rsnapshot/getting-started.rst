Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To configure :command:`rsnapshot` on a host using the :ref:`debops.rsnapshot`
role, that host needs to be included in the ``[debops_service_rsnapshot]``
Ansible inventory group:

.. code-block:: none

   [debops_service_rsnapshot]
   hostname

By default the role will create only the configuration for its own host, but
with the ``no_create_root`` option enabled - if the snapshot directory is not
present, the snapshots will not be created. You can either create the host
subdirectory in :file:`/var/cache/rsnapshot/hosts/` directory to enable the
snapshots, or change the configuration to point the snapshot directory to
removable media.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rsnapshot`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rsnapshot.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::rsnapshot``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.rsnapshot`` Ansible role:

- Manual pages: :man:`rsnapshot(1)`, :man:`rsync(1)`
