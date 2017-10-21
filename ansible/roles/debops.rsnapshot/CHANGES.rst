Changelog
=========

v0.1.7
------

*Released: 2015-11-29*

- Be more restrictive about log files on clients. Only allow members of the
  ``adm`` group read access. [ypid]

- Add ``/var/agentx`` and ``/swapfile*`` to list of excluded paths. [drybjed]

- Make sure that assymetric host configuration works on Ansible v2. [drybjed]

- Make sure that role works without ``debops.core`` configuration. [drybjed]

- Redesign the ``rsnapshot`` execution scripts.

  Instead of multiple scripts launched from ``cron``, role now uses single
  ``rsnapshot-scheduler`` script to prepare backups jobs and start them using
  ``batch`` command when available. The scheduler script gets the configuration
  of a particular backup job from the ``rsnapshot.conf`` configuration file of
  each host, and because of that different retain values are not hardcoded and
  depend entirely on the ``rsnapshot`` configuration.

  If ``batch`` is not installed, backup jobs will be scheduler with random
  pause using ``sleep``, meant to lessen the impact of multiple jobs running at
  once.

  Old ``rsnapshot`` scripts are not removed with this update, but changes to
  the scripts executed by ``cron`` should ensure that they are not executed.
  But you should still check if everything works correctly. [drybjed]

- Change how list of snapshots is defined.

  Instead of separate static variable for each snapshot (hourly, daily, weekly,
  monthly), list of snapshots is now defined using dictionary variables. This
  allows definition of different snapshot lists or creation of differently
  scheduled snapshots. [drybjed]

- Use more inventory group names to define which hosts are clients and which
  are servers. [drybjed]

- Add ``rsnapshot_ssh_port`` variable. This allows management of SSH public
  keys and host fingerprints on hosts with non-default SSH port. [drybjed]

- Various updates in ``renspahost-scheduler`` script.

  Scheduler PID files are now stored in separate ``/run/rsnapshot-scheduler/``
  subdirectory. Scheduler stores the PID of its process for each backup job
  before scheduling it using ``batch`` or ``sleep``, therefore repeated
  execution of the scheduler script won't result in multiple backup jobs of the
  same type.

  Scheduler logs are now more verbose, you can see each operation as it
  happens.

  Because ``batch`` processes submitted jobs in order, scheduler now randomizes
  list of hosts to make backup jobs less repetitive and hopefully less resource
  intensive in the long run. [drybjed]

- Remote hosts are now configured in separate directory, by default
  ``/etc/rsnapshot/hosts/``. Old configuration won't be moved automatically,
  but reconfiguring the host using Ansible should create the new one correctly.
  [drybjed]

- Update role tags to current format. [drybjed]

- Allow modification of scheduler ``batch`` command, as well as selection of
  the ``at`` queue to use. [drybjed]

- Split ``rsnapshot_exclude_default`` variable into more manageable parts.
  [drybjed]

- Fix ``ssh-keyscan`` command to correctly scan host SSH fingerprints.
  [drybjed]

- Update role documentation. [drybjed]

v0.1.6
------

*Released: 2015-06-11*

- Add ``rsnapshot_cmd_rsync`` variable which allows you to set the path to
  a script executed during backup. [drybjed]

- Add ``rsync-no-vanished`` wrapper script, which bypasses an issue when `files
  during long backups vanish`_ and the backup cycle is broken. It's set to be
  run by default for all hosts, can be overridden per host. [drybjed]

.. _files during long backups vanish: https://bugzilla.samba.org/show_bug.cgi?id=3653

v0.1.5
------

*Released: 2015-04-30*

- Add :file:`/lib32` directory to the list of default excluded directories.
  [drybjed]

- Disable ``ssh_args`` setting on Debian Jessie due to `Debian Bug #717451`_ to
  allow backups to run. It will be re-enabled when a fix is released in future
  Jessie point release. [drybjed]

.. _Debian Bug #717451: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=717451

v0.1.4
------

*Released: 2015-03-19*

- Add a way to reset known SSH host fingerprints in case that hosts are
  reinstalled or other related issues are occurring. [drybjed]

v0.1.3
------

*Released: 2015-02-26*

- Role will ignore other `:program:`rsnapshot` client hosts while configuring the
  servers. This allows multiple `:program:`rsnapshot` clients to exist in
  ``[debops_rsnapshot]`` group and other groups without issues. [drybjed]

- You can create a client host without internal servers by setting
  ``rsnapshot_servers: '{{ groups.debops_rsnapshot }}'`` in inventory for this
  host. It can then be used to backup only external hosts, if needed. [drybjed]

v0.1.2
------

*Released: 2015-02-26*

- ``rsnapshot_one_fs`` default value is set to ``0`` to enable backups across
  filesystems. This is less surprising and makes sure that everything that
  should be backed up, is backed up by default. [drybjed]

- Add more OpenVZ directories to includes/excludes. [drybjed]

v0.1.1
------

*Released: 2015-02-23*

- Scan SSH fingerprints separately from hosts with custom backup hostname,
  otherwise Ansible throws an error about missing dict key in list of results
  [drybjed]

v0.1.0
------

*Released: 2015-02-22*

- Initial release [drybjed]

