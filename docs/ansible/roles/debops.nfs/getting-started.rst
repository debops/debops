Getting started
===============

Default configuration
---------------------

The role does not specify any NFS shares by default, you need to configure them
using the provided variables (see :ref:`nfs__ref_shares` for more details).

The configured NFS shares should exist and be available prior to the role
execution, otherwise Ansible will hang waiting for the finished
:command:`mount` command. You can use the ``debops.nfs_server`` role to
configure NFS4 shares.

Example inventory
-----------------

To enable NFS support on a host it needs to be included in the specific Ansible
inventory group:

.. code-block:: none

   [debops_service_nfs]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nfs`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nfs.yml
   :language: yaml
