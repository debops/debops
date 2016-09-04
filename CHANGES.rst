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

- Moved sysctl parts from debops.console_ to a separate ``debops.sysctl``
  role. [ypid_]


v0.1.2
------

*Released: 2016-05-26*

- Remove list of additional APT packages to install. This functionality has
  been moved to the ``debops.apt_install`` Ansible role. [drybjed]

- Change how the preferred text editor is selected. Instead of specifying
  a preferred editor, role contains a list of preferred editors and checks it
  against a list of installed editors. The first found editor is selected as
  the preferred one. [drybjed]

v0.1.1
------

*Released: 2016-02-18*

- Fix a bug with wrong ``ansible_local.proc.hidepid_group`` value when hidepid
  was not enabled in ``/proc``. [prahal]

- Be more strict in parsing ``/proc/mounts`` when looking for a ``/proc`` entry
  with enabled ``hidepid=`` parameter. [drybjed]

v0.1.0
------

*Released: 2016-02-07*

- Add Changelog. [drybjed]

- Change default NFS filesystem type from ``nfs4`` to ``nfs``, system
  automatically picks the correct type. [drybjed]

- Add a way to manage entries in ``/etc/hosts``. [drybjed]

- Add a task that allows to copy custom files from Ansible Controller, list of
  files is configurable using Ansible inventory. [drybjed]

- Add support for setting default system-wide locale. [drybjed]

- Add option to configure system-wide ``editor`` alternative. [drybjed]

- Tag various tasks for convenient use. [drybjed]

- Ensure mount directories exist when manually mounted. [ypid]

- Add kernel parameter configuration and shared memory configuration.

  Amount of shared memory limits starting with Linux kernel 3.16 is ridiculusly
  high by default. This configuration limits the shared memory size to
  reasonable amounts depending on available system RAM. More information:
  https://git.kernel.org/cgit/linux/kernel/git/mhocko/mm.git/commit/include/uapi/linux/shm.h?id=060028bac94bf60a65415d1d55a359c3a17d5c31
  [drybjed]

- Install additional packages by default: ``mtr-tiny``, ``tree``, ``at``.
  Install ``nfs-common`` if NFS mounts are configured.  [drybjed]

- Protect the Tab characters in ``lineinfile`` module. [drybjed]

- Remove the ``at`` package from list of installed packages, it's now managed
  by separate ``debops.atd`` role. [drybjed]

- Create list of conditionally installed packages. [drybjed]

- Install ``libpam-systemd`` on hosts managed by ``systemd`` init. This
  provides better support for user sessions which will be moved to their own
  separate cgroups. Users are also able to create their own ``systemd``
  services, timers, and other units. [drybjed]

- Add support for ``sysnews`` package, useful on multiuser systems. [drybjed]

- Fix deprecation warnings on Ansible 2.1.0. [drybjed]

- Make sure that ``systemd-logind`` service is included in the ``procadmins``
  system group when ``/proc`` ``hidepid`` option is enabled. [drybjed]

- Add ``proc.fact`` fact script which contains information about ``hidepid``
  options for other Ansible roles to use. [drybjed]
