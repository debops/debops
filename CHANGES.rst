Changelog
=========

.. include:: includes/all.rst

**debops.lxc**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.lxc master`_ - unreleased
---------------------------------

.. _debops.lxc master: https://github.com/debops/ansible-lxc/compare/v0.1.0...master


debops.lxc v0.1.0 - 2016-11-22
------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Add APT preference for backported ``initramfs-tools`` on Debian Wheezy,
  required by newer Linux kernel packages, also backported from Jessie.
  [drybjed_]

- Allow setting default OS release created by the :command:`lxc-debops` template.
  By default the host release will be used as the container release. [drybjed_]

- Add variables to configure administrator account home directory group and
  permissions. By default, home directory will be owned by ``admins`` group
  with ``0750`` permissions. [drybjed_]

Changed
~~~~~~~

- Redesign admin account and SSH key configuration in new LXC containers.

  Admin account can now be enabled or disabled using separate
  ``lxc_template_admin`` variable. By default, a system account will be created
  (with UID < 1000) with home in :file:`/var/local/` directory to avoid clashes
  with :file:`/home` directories. You can also specify default shell. [drybjed_]

- Switch from creation of 1 system group to a list of system groups that are
  created if not present. Administrator account will be added to all specified
  system groups. [drybjed_]

- Modify :command:`sudo` configuration to specify the name of the group that is
  configured to have passwordless access to all commands. By default first
  group specified in ``lxc_template_admin_groups`` will be granted full access.
  [drybjed_]

- Change the container bootstrap function to only create or modify admin
  account if it's not already present in container. [drybjed_]

- Mask :file:`/lib/systemd/system/getty-static.service` in new LXC containers. This
  unit starts 6 ``getty`` services by default if ``dbus`` is not installed; LXC
  containers have 4 static ``getty.service`` units configured instead. This
  will stop ``getty-static.service`` from spamming the logs. [drybjed_]

- Mask :file:`/lib/systemd/system/proc-sys-fs-binfmt_misc.automount` in new LXC
  containers. Containers cannot directly mount filesystems, a separate wrapper
  needs to be used. [drybjed_]

- Change the SSH public key lookup to avoid issues when :command:`ssh-add` does not
  return any keys. Thanks, xorgic! [drybjed_]

- Allow to use mirror/proxy for security.debian.org as well. [ypid_]

- Switched the default Debian mirror to the new official redirector at
  ``http://httpredir.debian.org/``. [ypid_]

- Correctly detect the container admin account name on Ansible v2. [drybjed_]

Removed
~~~~~~~

- Remove the ``debops_lxc`` Ansible inventory group. Make sure you hosts
  are in ``debops_service_lxc``. [ypid_]

- Remove all of the Ansible role dependencies.

  Configuration of dependent services like firewall, TCP Wrappers is set in
  separate default variables. These variables can be used by the Ansible
  playbooks to configure settings related to ``dnsmasq`` in other services.
  [ypid_]

- Dropped debops.backporter_ usage and Debian Wheezy support. [ypid_]
