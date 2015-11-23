Changelog
=========

v0.1.7
------

*Unreleased*

- Be more restrictive about log files on clients. Only allow members of the
  ``adm`` group read access. [ypid]

- Add ``/var/agentx`` and ``/swapfile*`` to list of excluded paths. [drybjed]

- Make sure that assymetric host configuration works on Ansible v2. [drybjed]

- Make sure that role works without ``debops.core`` configuration. [drybjed]

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

