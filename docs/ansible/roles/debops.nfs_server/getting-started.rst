Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The role by default focuses on the NFSv4 support. The NFSv3 support can be
enabled by setting the :envvar:`nfs_server__v3` variable to ``True``.
The Kerberos support is not fully implemented at this point.

By default role expects a list of allowed clients in the
:envvar:`nfs_server__allow` variable. Example:

.. code-block:: yaml

   nfs_server__allow: [ '192.0.2.0/24' ]

When this list is not empty and contains IP addresses or CIDR subnets, the role
will allow access to the ``nfs`` service through the firewall and cofigure NFS
exports in the :file:`/etc/exports.d/ansible.exports` configuration file. Only the
NFS root pseudo filesystem is defined by default, in the :file:`/srv/nfs/`
directory. You should define additional exports, for example:

.. code-block:: yaml

   nfs_server__exports:
     - path: '/srv/nfs/shared'
       acl: '192.0.2.0/24'
       options: 'rw,no_subtree_check,no_root_squash'

check the :ref:`nfs_server__ref_exports` documentation for more details.

You can mount the above NFS share on other hosts by using the commands:

.. code-block:: console

   mkdir -p /media/nfs/shared
   mount -t nfs4 -o proto=tcp,port=2049,_netdev hostname:/shared /media/nfs/shared

You can also add an entry in the :file:`/etc/fstab` configuration file:

.. code-block:: none

   hostname:/shared   /media/nfs/shared   nfs4   noatime,nosuid,hard,intr,proto=tcp,port=2049,_netdev   0   0

Refer to the :ref:`debops.nfs` role for information about how to configure NFS shares
on other hosts using Ansible.


Example inventory
-----------------

To enable NFS server support on a host, it needs to be included in the Ansible
inventory in a specific group:

.. code-block:: none

   [debops_service_nfs_server]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nfs_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nfs_server.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::nfs_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
