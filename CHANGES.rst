Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog [drybjed]

- Uninstall conflicting packages before installing the requested ones. This
  should fix `ntp and AppArmor issue`_ present in Ubuntu. [drybjed]

- Fixed ``ntp_listen: '*'`` for NTPd. [ypid]

.. _ntp and Apparmor issue: https://bugs.launchpad.net/ubuntu/+source/openntpd/+bug/458061

