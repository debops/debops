.. _borgbackup__ref_backup_server:

Setup the backup server
=======================

To setup a backup server, choose a group name for example
``[backup_server]`` and add the backup servers to it:

.. code-block:: none

   [backup_server]
   backup.example.net


Configure the backup server in the ``backup_server`` host group inventory:

.. literalinclude:: inventory/group_vars/backup_server.yml
   :language: yaml


On each backup server, you will need to create user accounts that can be used
to store, delete and retrieve backups. Configure them in
:file:`inventory/host_vars/backup.example.net/generated.yml` for example:

.. literalinclude:: inventory/host_vars/backup.example.net/generated.yml
   :language: yaml

With this configuration, the root account of db.example.net can run
:command:`borg serve` via ssh on the backup server. The ssh key is managed by
the :ref:`debops.root_account` role.

The following script can be used to generate the last inventory file:

.. literalinclude:: scripts/gen_ssh_keys_for_server_backup
   :language: shell

You might come up with a better, Ansible-integrated solution for this. If you
do, please mentioned it here in the docs.

With this, the backup server should be ready after you run the full DebOps
playbook against it.
