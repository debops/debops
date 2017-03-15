Changelog
=========

**debops.fail2ban**

.. include:: includes/all.rst

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.fail2ban master`_ - unreleased
--------------------------------------

.. _debops.fail2ban master: https://github.com/debops/ansible-fail2ban/compare/v0.1.1...master

Changed
~~~~~~~

- Harmonize role behaviour on Debian and Ubuntu. Disable the default `ssh` jail
  defined in the upstream :file:`jail.conf` on Debian. Rename the disabled
  `ssh-iptables` jail on Ubuntu to `ssh`. Ubuntu users which depend on the
  definition of the `ssh-iptables` jail in :file:`jail.conf` must adjust their
  configuration. [ganto_]

- Enable SSH jail via default configuration of :envvar:`fail2ban_jails`. [ganto_]


`debops.fail2ban v0.1.1`_ - 2016-12-01
--------------------------------------

.. _debops.fail2ban v0.1.1: https://github.com/debops/ansible-fail2ban/compare/v0.1.0...v0.1.1

Added
~~~~~

- Added filter for ownCloud logs [scibi]

- Add support for custom local actions and filters. [carlalexander]

Changed
~~~~~~~

- Restart fail2ban service instead of reloading it (required for Jessie) [scibi]

Fixed
~~~~~

- Remove Ansible 2.1 deprecation warnings. [carlalexander]

- Fix log level error in :command:`fail2ban` logs. [prahal]


debops.fail2ban v0.1.0 - 2015-04-10
-----------------------------------

Added
~~~~~

- Initial release [drybjed_]

