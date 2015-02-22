Getting started
===============

.. contents::
   :local:

Required Ansible host groups
----------------------------

``[debops_rsnapshot]``
  Defines a group of hosts which will be configured as "clients".

  These hosts will have ``rsnapshot`` installed and will connect to configured
  "servers" at random times through the day, synchronize the specified files
  and rotate archived snapshots.

  You want them to have lots of disk space depending on your configuration,
  preferably encrypted. You can have multiple clients configured in parallel.

  This group can be redefined in :envvar:`rsnapshot_clients` if needed.


``[debops_rsnapshot_rsync]``
  Defines a group of hosts which are configured as "servers".

  These hosts will have ``rsync`` installed, and SSH keys from clients will be
  configured on the server ``root`` account to allow unrestricted access from
  the client.

  A ``rrsync`` script provided with ``rsync`` package will be installed to
  permit for restricted, read-only access using an SSH command stored in
  ``~/.ssh/authorized_keys``.

  This group can be redefined in :envvar:`rsnapshot_servers` if needed.


Both host groups can be configured either directly (with hosts), or as a parent
group for other groups. You probably want a mixed set of ``[debops_rsnapshot]``
as a list of specific hosts and ``[debops_rsnapshot_rsync:children]`` pointing
to other groups of hosts to be backed up. This way new hosts added to your
primary groups can be automatically prepared to be backed up.


Default directories
-------------------

Configuration files are stored in ``/etc/rsnapshot/`` directory.

Backups are stored by default in ``/var/cache/rsnapshot/`` directory.


Example inventory
-----------------

This inventory will tell Ansible to backup all hosts in ``[all_hosts]`` group
except the ``archive`` host, to the ``archive`` host::

    [all_hosts]
    alpha
    beta
    archive

    [debops_rsnapshot]
    archive

    [debops_rsnapshot_rsync:children]
    all_hosts

Example playbook
----------------

::

    ---

    - name: Manage rsnapshot backups
      hosts: debops_rsnapshot:debops_rsnapshot_rsync

      roles:
        - role: debops.rsnapshot
          tags: rsnapshot

When the inventory is set up, run Ansible on all of the hosts in both groups to
have them correctly configured::

    debops -t rsnapshot

You might want to see :doc:`list of default variables <defaults>` to change how
``rsnapshot`` is configured, and a separate :doc:`advanced guides <guides>` to
see how you can use the role in different environments.

