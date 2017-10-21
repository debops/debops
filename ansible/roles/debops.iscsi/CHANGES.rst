Changelog
=========

v0.1.1
------

*Released: 2016-02-10*

- Add a configuration variable for ``debops.unattended_upgrades`` role which
  adds the ``open-iscsi`` package to list of blacklisted packages so that it
  will not be upgraded automatically. [drybjed]

- Remove hard dependency on ``debops.lvm`` role. It can be used through the
  Ansible playbook if needed. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Update documentation. [drybjed]

- Update all of the role variables to have a distinct namespace. [drybjed]

v0.1.0
------

*Released: 2015-07-17*

- Initial release. [drybjed]

