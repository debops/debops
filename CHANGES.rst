Changelog
=========

.. include:: includes/all.rst

**debops.console**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.console master`_ - unreleased
-------------------------------------

.. _debops.console master: https://github.com/debops/ansible-console/compare/v0.1.2...master

Changed
~~~~~~~

- Moved sysctl parts from debops.console_ to a separate debops.sysctl_
  role. [ypid_]


v0.1.2
------

*Released: 2016-05-26*

- Remove list of additional APT packages to install. This functionality has
  been moved to the debops.apt_install_ Ansible role. [drybjed_]

- Change how the preferred text editor is selected. Instead of specifying
  a preferred editor, role contains a list of preferred editors and checks it
  against a list of installed editors. The first found editor is selected as
  the preferred one. [drybjed_]

v0.1.1
------

*Released: 2016-02-18*

- Fix a bug with wrong ``ansible_local.proc.hidepid_group`` value when hidepid
  was not enabled in :file:`/proc`. [prahal]

- Be more strict in parsing :file:`/proc/mounts` when looking for a :file:`/proc` entry
  with enabled ``hidepid=`` parameter. [drybjed_]

v0.1.0
------

*Released: 2016-02-07*

- Add Changelog. [drybjed_]

- Change default NFS filesystem type from ``nfs4`` to ``nfs``, system
  automatically picks the correct type. [drybjed_]

- Add a way to manage entries in :file:`/etc/hosts`. [drybjed_]

- Add a task that allows to copy custom files from Ansible Controller, list of
  files is configurable using Ansible inventory. [drybjed_]

- Add support for setting default system-wide locale. [drybjed_]

- Add option to configure system-wide ``editor`` alternative. [drybjed_]

- Tag various tasks for convenient use. [drybjed_]

- Ensure mount directories exist when manually mounted. [ypid_]

- Add kernel parameter configuration and shared memory configuration.

  Amount of shared memory limits starting with Linux kernel 3.16 is ridiculusly
  high by default. This configuration limits the shared memory size to
  reasonable amounts depending on available system RAM. More information:
  https://git.kernel.org/cgit/linux/kernel/git/mhocko/mm.git/commit/include/uapi/linux/shm.h?id=060028bac94bf60a65415d1d55a359c3a17d5c31
  [drybjed_]

- Install additional packages by default: ``mtr-tiny``, ``tree``, ``at``.
  Install ``nfs-common`` if NFS mounts are configured.  [drybjed_]

- Protect the Tab characters in ``lineinfile`` module. [drybjed_]

- Remove the ``at`` package from list of installed packages, it's now managed
  by separate debops.atd_ role. [drybjed_]

- Create list of conditionally installed packages. [drybjed_]

- Install ``libpam-systemd`` on hosts managed by ``systemd`` init. This
  provides better support for user sessions which will be moved to their own
  separate cgroups. Users are also able to create their own ``systemd``
  services, timers, and other units. [drybjed_]

- Add support for ``sysnews`` package, useful on multiuser systems. [drybjed_]

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]

- Make sure that ``systemd-logind`` service is included in the ``procadmins``
  system group when :file:`/proc` ``hidepid`` option is enabled. [drybjed_]

- Add ``proc.fact`` fact script which contains information about ``hidepid``
  options for other Ansible roles to use. [drybjed_]
