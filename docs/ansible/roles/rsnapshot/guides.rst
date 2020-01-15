Guides and examples
===================

.. contents::
   :local:

Role design goals
-----------------

Host backups performed by the :program:`rsnapshot` script are a very efficient
method to keep time-based snapshots of local or remote systems. Unfortunately,
the default method of creating backups using one configuration file and backing
up remote hosts in order is inconvenient: all hosts managed through this single
file will be backed up each time, there's only one set of snapshots that can be
used this way, and any error will stop backups of hosts further along the
config file.

To avoid this issue, the :ref:`debops.rsnapshot` role uses combination of
:man:`batch(1)`, :man:`cron(8)` and custom scheduler script written in Bash to
perform backups of multiple remote hosts at the same time, each one configured
in its own :file:`rsnapshot.conf` configuration file, with its own lists of
snapshots to manage, its own include/exclude lists, and so on.

How rsnapshot backups are performed
-----------------------------------

The whole backup sequence is:

1. :program:`cron` launches :program:`rsnapshot-wrapper` script with
   a specified interval (hourly, daily, weekly, monthly). Custom intervals are
   also possible, but not implemented at this time.

2. :program:`rsnapshot-wrapper` launches the :program:`rsnapshot-scheduler`
   script, requesting a ``schedule`` operation for a given backup interval for
   all subdirectories found in the :file:`/etc/rsnapshot/hosts/` directory,
   a given subdirectory represents one host to back up.

3. :program:`rsnapshot-scheduler` scans :file:`/etc/rsnapshot/hosts/`
   subdirectories looking for configuration files, and checks if a given
   configuration uses specific interval - for example when a ``hourly``
   interval is executed, script checks if ``retain hourly`` is present in the
   :file:`rsnapshot.conf` configuration file.

4. :program:`rsnapshot-scheduler` checks if current backup interval for a given
   host is already scheduled using a pidfile in
   :file:`/run/rsnapshot-scheduler/` directory. If one is found, script
   finishes gracefully to not create duplicate backup jobs.

5. If current interval is found and particular configuration is not disabled
   (file :file:`/etc/rsnapshot/hosts/<host>/{stop|disable|disabled}` is
   absent), :program:`rsnapshot-scheduler` creates a "backup job" for a given
   host. If :program:`at` is installed, backup job will be added to the
   :program:`batch` queue; otherwise, a background instance of
   :program:`rsnapshot-scheduler` will be started with a random short
   :program:`sleep` interval to not create high load spikes on the backup
   machine when multiple backups are scheduled at the same time.

6. If :program:`at` is installed, it will start backup jobs in order depending
   on the current system load (you can use the :ref:`debops.atd` role to manage
   that).  Depending on available CPU cores and system load, backups might be
   done within the selected interval (hourly, for example). If not, duplicate
   backup jobs won't be created as long as the previous backup job is queued.

7. On the next specified interval, :program:`cron` will run the
   :program:`rsnapshot-scheduler` again, scheduling new backup jobs.


.. _rsnapshot_external_servers:

How to backup hosts outside of Ansible cluster
----------------------------------------------

In addition to backing up hosts under Ansible control, you might want to create
configuration for backing up other hosts, which you don't want to configure
directly (or can't). For this situation, you can use perform the steps
described below to prepare the hosts for periodic snapshotting.

Things to set up on external host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For practical reasons, :program:`rsnapshot` should use a ``root`` account
directly on remote host. To make this configuration more secure, you can use
:command:`rrsync` Perl script provided with the `rsync`_ package, which lets
you set up read-only access over SSH from remote hosts.

.. _rsync: https://rsync.samba.org/

First, on Debian-based systems, install :command:`rsync` package and extract
provided script to a convenient directory:

.. code-block:: console

   sudo apt install rsync
   sudo gzip -d -c /usr/share/doc/rsync/scripts/rrsync.gz > /usr/local/bin/rrsync
   sudo chmod +x /usr/local/bin/rrsync

When the :command:`rrsync` script is set up, you will have to add one of the
:command:`rsnapshot` SSH identities on the remote host, in the
:file:`~/.ssh/authorized_keys` file of the ``root`` account. The default SSH
identities are located in the :file:`~/.ssh/id_rsnapshot*.pub` files on the
:command:`rsnapshot` host. You should use the same SSH identity which you
configured with a given host using the ``item.ssh_identity`` parameter, or
``id_rsnapshot`` if you want to use the default one.

At the same time you will configure this key to only allow for a specific
:command:`rsync` command. You should include configuration similar to this in
:file:`/root/.ssh/authorized_keys`, in one line:

.. code-block:: none

   no-pty,no-agent-forwarding,no-X11-forwarding,no-port-forwarding,command="ionice -c 3 nice /usr/local/bin/rrsync -ro /" ssh-rsa AAAAB3NzaC1yc2EAAAA...

The :command:`ionice` and the :command:`nice` commands will prevent
:command:`rsync` from hogging too much system resources during its operation.

This will allow read-only access to whole filesystem. After that, you can run
the :ref:`debops.rsnapshot` Ansible role and it should correctly configure your
:program:`rsnapshot` client host to access external servers.

Fixing "stdin: is not a tty" issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On default Debian installation there is a problem - when :program:`rsnapshot`
tries to connect to the server, shell might respond with a warning:

.. code-block:: console

   stdin: is not a tty

This will prompt :program:`rsnapshot` to send an e-mail to system administrator
with the response, which might get annoying after a while. To avoid that, open
:file:`/root/.profile` file on an external host and change line:

.. code-block:: sh

   mesg n

to:

.. code-block:: sh

   tty -s && mesg n

This will tell shell that it should check if connection is interactive before
changing the terminal settings. This configuration is automatically applied on
hosts managed by DebOps by the :ref:`debops.root_account` Ansible role.
