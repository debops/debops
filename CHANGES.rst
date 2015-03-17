Changelog
=========

v0.1.3
------

*Released: 2015-02-26*

- Role will ignore other ``rsnapshot`` client hosts while configuring the
  servers. This allows multiple ``rsnapshot`` clients to exist in
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

