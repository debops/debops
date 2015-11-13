Changelog
=========

v0.1.0
------

*Released: 2015-11-13*

- Add Changelog [drybjed]

- Uninstall conflicting packages before installing the requested ones. This
  should fix `ntp and AppArmor issue`_ present in Ubuntu. [drybjed]

- Fixed ``ntp_listen: '*'`` for NTPd. [ypid]

- Added support for ``ntpdate``. [ypid]

.. _ntp and Apparmor issue: https://bugs.launchpad.net/ubuntu/+source/openntpd/+bug/458061

- Rewrite the installation tasks to work correctly on Ansible v2. [drybjed]

- Drop the dependency on ``debops.ferm`` Ansible role, firewall configuration
  is now defined in role default variables, and can be used by other roles
  through playbooks. [drybjed]

