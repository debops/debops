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
