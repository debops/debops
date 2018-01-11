Guides and examples
===================

.. contents::
   :local:

Role design goals
-----------------

Host backups performed by :program:`rsnapshot` are a very efficient method to
keep time-based snapshots of local or remote systems. Unfortunately, the default
method of creating backups using one configuration file and backing up remote
hosts in order is inconvenient: all hosts managed through this single file will
be backed up each time, there's only one set of snapshots that can be used this
way, and any error will stop backups of hosts further along the config file.

To avoid this issue, ``debops.rsnapshot`` role uses combination of
:program:`batch`, :program:`cron` and custom scheduler script written in Bash
to perform backups of multiple remote hosts at the same time, each one
configured in its own :file:`rsnapshot.conf` configuration file, with its own
lists of snapshots to manage, its own include/exclude lists, and so on.

How rsnapshot backups are performed
-----------------------------------

The whole backup sequence is:

1. :program:`cron` launches :program:`rsnapshot-wrapper` script with
   a specified interval (hourly, daily, weekly, monthly). Custom intervals are
   also possible, but not implemented at this time.

2. :program:`rsnapshot-wrapper` launches the :program:`rsnapshot-scheduler`
   script, requesting a ``schedule`` operation for a given backup interval for
   all hosts found in the :file:`/etc/rsnapshot/hosts/` directory.

3. :program:`rsnapshot-scheduler` scans :file:`/etc/rsnapshot/hosts/` directory
   looking for configuration files, and checks if a given configuration uses
   specific interval - for example when a ``hourly`` interval is executed,
   script checks if ``retain hourly`` is present in the :file:`rsnapshot.conf`
   configuration file.

4. :program:`rsnapshot-scheduler` checks if current backup interval for a given
   host is already scheduled using a pidfile in
   :file:`/run/rsnapshot-scheduler/` directory. If one is found, script
   finishes gracefully to not create duplicate backup jobs.

5. If current interval is found and particular configuration is not disabled
   (file :file:`/etc/rsnapshot/hosts/<host>/disabled` is absent),
   :program:`rsnapshot-scheduler` creates a "backup job" for a given host. If
   :program:`at` is installed, backup job will be added to the :program:`batch`
   queue; otherwise, a background instance of :program:`rsnapshot-scheduler`
   will be started with a random short :program:`sleep` interval to not create
   high load spikes on the backup machine when multiple backups are scheduled
   at the same time.

6. If :program:`at` is installed, it will start backup jobs in order depending
   on the current system load (you can use ``debops.atd`` role to manage that).
   Depending on available CPU cores and system load backups might be done
   within the selected interval (hourly, for example). If not, duplicate backup
   jobs won't be created as long as the previous backup job is queued.

7. On the next specified interval, :program:`cron` will run the
   :program:`rsnapshot-scheduler` again, scheduling new backup jobs.

.. _rsnapshot_external_servers:

How to backup hosts outside of Ansible cluster
----------------------------------------------

In addition to backing up hosts under Ansible control, you might want to create
configuration for backing up other hosts, which you don't want to configure
them directly (or can't). For this situation, you can use
:envvar:`rsnapshot_external_servers` list to configure external hosts in
a particular :program:`rsnapshot` client host.

Configuration of external hosts in Ansible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's an example configuration which will let you backup ``other.example.org``
host::

    rsnapshot_external_servers:

        # Required
      - name: 'other.example.org'

        # Optional
        sleep: '20'
        backup_user: 'root'
        ssh_args: '-p 22'

You can use most of the :doc:`variables <defaults>` that are defined in
``rsnapshot_`` namespace, just drop the ``rsnapshot_`` prefix.  ``item.name``
key is required and should be a FQDN hostname of the remote host you want to
backup.

Things to set up on external host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For practical reasons, :program:`rsnapshot` should use a ``root`` account directly on
remote host. To make this configuration more secure, you can use ``rrsync``
Perl script provided with `rsync`_ which lets you set up read-only access over
SSH from remote hosts.

.. _rsync: https://rsync.samba.org/

First, on Debian-based systems, install :command:`rsync` package and extract provided
script to a convenient directory::

    sudo apt-get install rsync
    sudo gzip -d -c /usr/share/doc/rsync/scripts/rrsync.gz > /usr/local/lib/rrsync
    sudo chmod +x /usr/local/lib/rrsync

After that, you will want to install the public SSH key from the ``root``
account of the client host to ``root`` account on the host you want to back up.
At the same time you will configure this key to only allow for a specific
:command:`rsync` command. You should include configuration similar to this in
:file:`/root/.ssh/authorized_keys`, in one line::

    no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding,command="ionice -c 3 nice /usr/local/lib/rrsync -ro /" ssh-rsa AAAAB3NzaC1yc2EAAAA...

``ionice`` and ``nice`` commands will prevent :command:`rsync` from hogging too much
system resources during its operation.

This will allow read-only access to whole filesystem. After that, you can run
``debops.rsnapshot`` Ansible role and it should correctly configure your
:program:`rsnapshot` client host to access external servers.

Fixing "stdin: is not a tty" issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On default Debian installation this creates a problem - when :program:`rsnapshot`
tries to connect to the server, shell might respond with a warning::

   stdin: is not a tty

This will prompt :program:`rsnapshot` to send an e-mail to system administrator with
the response, which might get annoying after a while. To avoid that, open
:file:`/root/.profile` file on an external host and change line::

   mesg n

to::

   tty -s && mesg n

This will tell shell that it should check if connection is interactive before
changing the terminal settings.


How to split different servers between backup hosts
---------------------------------------------------

If you are configuring multiple :program:`rsnapshot` client hosts, all of them will
back up all hosts from ``rsnapshot_servers`` group (but not each other).

If you want to split different hosts between various :program:`rsnapshot` clients, you
can do that using separate Ansible groups.

Here's an example Ansible inventory::

   # Main host group
   [all_hosts]
   alpha
   beta
   gamma
   delta
   archive-one
   archive-two

   # These hosts should be archived on 'archive-one'
   [archive_group_one]
   alpha
   beta

   # These hosts should be archived on 'archive-two'
   [archive_group_two]
   gamma
   delta

   # List of rsnapshot clients
   [debops_service_rsnapshot]
   archive-one
   archive-two

   # List of rsnapshot servers
   [debops_service_rsnapshot_rsync:children]
   archive_group_one
   archive_group_two

Now, with this inventory in place, you can tell the :program:`rsnapshot` client hosts
which host group to use for their servers::

    # In host_vars/archive-one/rsnapshot.yml:
    rsnapshot_servers: '{{ groups.archive_group_one }}'

    # In host_vars/archive-two/rsnapshot.yml:
    rsnapshot_servers: '{{ groups.archive_group_two }}'

This will make ``debops.rsnapshot`` only configure :command:`rsync` servers on their
respectful :program:`rsnapshot` clients.

