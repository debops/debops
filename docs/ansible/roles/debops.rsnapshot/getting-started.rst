Getting started
===============

.. contents::
   :local:

Required Ansible host groups
----------------------------

``[debops_service_rsnapshot]`` or ``[debops_service_rsnapshot_clients]``
  Defines a group of hosts which will be configured as "clients".

  These hosts will have :program:`rsnapshot` installed and will connect to the
  configured "servers" at specified times through the day, synchronize the
  files and rotate archived snapshots.

  You want them to have lots of disk space depending on your configuration,
  preferably encrypted. You can have multiple clients configured in parallel.

  This group can be redefined in :envvar:`rsnapshot_clients` if needed.


``[debops_service_rsnapshot_rsync]`` or ``[debops_service_rsnapshot_servers]``
  Defines a group of hosts which are configured as "servers".

  These hosts will have :command:`rsync` installed, and SSH keys from clients
  will be configured on the server ``root`` account to allow unrestricted
  access from the client.

  A ``rrsync`` script provided with the :command:`rsync` package will be
  installed to permit for restricted, read-only access using an SSH command
  stored in ``~/.ssh/authorized_keys``.

  This group can be redefined in :envvar:`rsnapshot_servers` if needed.


Both host groups can be configured either directly (with hosts), or as a parent
group for other groups. You probably want a mixed set of
``[debops_service_rsnapshot]`` as a list of specific hosts and
``[debops_service_rsnapshot_rsync:children]`` pointing to other groups of hosts
to be backed up. This way new hosts added to your primary groups can be
automatically prepared to be backed up.


Default directories
-------------------

Configuration files are stored in :file:`/etc/rsnapshot/hosts/` directory.

Backups are stored by default in :file:`/var/cache/rsnapshot/` directory.


Example inventory
-----------------

This inventory will tell Ansible to backup all hosts in ``[all_hosts]`` group
except the ``archive`` host, to the ``archive`` host::

    [all_hosts]
    alpha
    beta
    archive

    [debops_service_rsnapshot]
    archive

    [debops_service_rsnapshot_rsync:children]
    all_hosts

Example playbook
----------------

.. literalinclude:: ../../../../ansible/playbooks/service/rsnapshot.yml
   :language: yaml

When the inventory is set up, run Ansible on all of the hosts in both groups to
have them correctly configured::

    debops -t role::rsnapshot

You might want to see :doc:`list of default variables <defaults>` to change how
`:program:`rsnapshot` is configured, and a separate :doc:`advanced guides
<guides>` to see how you can use the role in different environments.
