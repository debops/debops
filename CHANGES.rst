Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Support "stacked inventory variables" for APT sources, repositories, keys and
  lists of mirrors. [drybjed]

- Switch the default Debian mirror to new official redirector at
  ``http://httpredir.debian.org/``. [drybjed]

- Added ``apt_remove_default_configuration`` option which defaults to true.
  This ensures that ``/etc/apt/apt.conf`` is absent. [ypid]

- Use backported apt-cacher-ng on Debian Jessie. [ypid]

- Allow to modify APT sections without defining ``apt_default_sources`` by
  using the added ``apt_sources_sections`` variable. [ypid]

- Remove support for ``unattended-upgrades``. The new role
  ``debops.unattended_upgrades`` handles this now. The ``debops.apt`` role will
  have a task for some time which removes old configuration files related to
  ``unattended-upgrades`` to clean up the old systems. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

