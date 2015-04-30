Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Add APT preference for backported ``initramfs-tools`` on Debian Wheezy,
  required by newer Linux kernel packages, also backported from Jessie.
  [drybjed]

- Allow setting default OS release created by the ``lxc-debops`` template.
  By default the host release will be used as the container release. [drybjed]

- Redesign admin account and SSH key configuration in new LXC containers.

  Admin account can now be enabled or disabled using separate
  ``lxc_template_admin`` variable. By default, a system account will be created
  (with UID < 1000) with home in ``/var/local/`` directory to avoid clashes
  with ``/home`` directories. You can also specify default shell. [drybjed]

