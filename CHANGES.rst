Changelog
=========

v0.2.0
------

*Unreleased*

- Remove ``tasks/backup.yml`` and ``tasks/restore.yml``, they are not used in
  main role task list. [drybjed]

- Request ``sudo`` access on Travis-CI. [drybjed]

- Update documentation. [drybjed]

- Remove ``debops.auth`` role dependency. Configuration done by this role is
  assumed to be present, since it's executed as part of the ``common.yml``
  playbook. [drybjed]

- Add ``debops.secret`` role dependency, it's needed for access to LDAP
  secrets. [drybjed]

- Add ``debops.apt_preferences`` role dependency. OpenSSH from
  ``wheezy-backports`` will be installed on Debian Wheezy, if the repository is
  present. This brings version parity with Debian Jessie (current Stable), adds
  support for better encryption ciphers and allows to look up SSH public keys
  in external authentication sources. [drybjed]

- Add separate ``sshd_ferm_ports`` variable which is a list that defines what
  ports are opened in the firewall for access to OpenSSH server. By default
  only ``ssh`` port from ``/etc/services`` is opened. [drybjed]

- Add tags for ``debops.tcpwrappers`` and ``debops.sshkeys`` role depenencies.
  [drybjed]

v0.1.0
------

*Released: 2015-08-10*

- Add Changelog. [drybjed]

