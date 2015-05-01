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

- Switch from creation of 1 system group to a list of system groups that are
  created if not present. Administrator account will be added to all specified
  system groups. [drybjed]

- Modify ``sudo`` configuration to specify the name of the group that is
  configured to have passwordless access to all commands. By default first
  group specified in ``lxc_template_admin_groups`` will be granted full access.
  [drybjed]

