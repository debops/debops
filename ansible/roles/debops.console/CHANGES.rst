Changelog
=========

.. include:: includes/all.rst

**debops.console**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.console master`_ - unreleased
-------------------------------------

.. _debops.console master: https://github.com/debops/ansible-console/compare/v0.1.3...master

Added
~~~~~

- Support to remove host entries using ``console_hosts`` without specifying a
  ``value``. [ypid_]


Changed
~~~~~~~

- Configure the ``FSCKFIX`` parameter only on OS distribution releases that
  support it. [drybjed_]

Removed
~~~~~~~

- Remove support for ``root`` system account management. This functionality has
  been moved to a separate debops.root_account_ Ansible role. [drybjed_]

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


`debops.console v0.1.3`_ - 2016-11-07
-------------------------------------

.. _debops.console v0.1.3: https://github.com/debops/ansible-console/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Moved sysctl parts from ``debops.console`` to a separate debops.sysctl_
  role. [ypid_]

- Update documentation and Changelog. [drybjed_]

Fixed
~~~~~

- Fix the issue of the :command:`sysnews` task failing on Ansible v2.2 with
  empty news variable. [drybjed_]


`debops.console v0.1.2`_ - 2016-05-26
-------------------------------------

.. _debops.console v0.1.2: https://github.com/debops/ansible-console/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Change how the preferred text editor is selected. Instead of specifying
  a preferred editor, role contains a list of preferred editors and checks it
  against a list of installed editors. The first found editor is selected as
  the preferred one. [drybjed_]

Removed
~~~~~~~

- Remove list of additional APT packages to install. This functionality has
  been moved to the debops.apt_install_ Ansible role. [drybjed_]


`debops.console v0.1.1`_ - 2016-02-18
-------------------------------------

.. _debops.console v0.1.1: https://github.com/debops/ansible-console/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Be more strict in parsing :file:`/proc/mounts` when looking for a :file:`/proc` entry
  with enabled ``hidepid=`` parameter. [drybjed_]

Fixed
~~~~~

- Fix a bug with wrong ``ansible_local.proc.hidepid_group`` value when hidepid
  was not enabled in :file:`/proc`. [prahal]


debops.console v0.1.0 - 2016-02-07
----------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Add a way to manage entries in :file:`/etc/hosts`. [drybjed_]

- Add a task that allows to copy custom files from Ansible Controller, list of
  files is configurable using Ansible inventory. [drybjed_]

- Add support for setting default system-wide locale. [drybjed_]

- Add option to configure system-wide ``editor`` alternative. [drybjed_]

- Add kernel parameter configuration and shared memory configuration.

  Amount of shared memory limits starting with Linux kernel 3.16 is ridiculously
  high by default. This configuration limits the shared memory size to
  reasonable amounts depending on available system RAM. More information:
  https://git.kernel.org/cgit/linux/kernel/git/mhocko/mm.git/commit/include/uapi/linux/shm.h?id=060028bac94bf60a65415d1d55a359c3a17d5c31
  [drybjed_]

- Install additional packages by default: ``mtr-tiny``, ``tree``, ``at``.
  Install ``nfs-common`` if NFS mounts are configured.  [drybjed_]

- Create list of conditionally installed packages. [drybjed_]

- Install ``libpam-systemd`` on hosts managed by ``systemd`` init. This
  provides better support for user sessions which will be moved to their own
  separate cgroups. Users are also able to create their own ``systemd``
  services, timers, and other units. [drybjed_]

- Add support for ``sysnews`` package, useful on multiuser systems. [drybjed_]

- Add ``proc.fact`` fact script which contains information about ``hidepid``
  options for other Ansible roles to use. [drybjed_]

Changed
~~~~~~~

- Change default NFS filesystem type from ``nfs4`` to ``nfs``, system
  automatically picks the correct type. [drybjed_]

- Tag various tasks for convenient use. [drybjed_]

- Ensure mount directories exist when manually mounted. [ypid_]

- Protect the Tab characters in ``lineinfile`` module. [drybjed_]

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]

- Make sure that ``systemd-logind`` service is included in the ``procadmins``
  system group when :file:`/proc` ``hidepid`` option is enabled. [drybjed_]

Removed
~~~~~~~

- Remove the ``at`` package from list of installed packages, it's now managed
  by separate debops.atd_ role. [drybjed_]
