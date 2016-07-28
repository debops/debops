Changelog
=========

**debops.ntp**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.ntp master`_ - unreleased
---------------------------------

.. _debops.ntp master: https://github.com/debops/ansible-ntp/compare/v0.2.2...master


`debops.ntp v0.2.2`_ - 2016-07-28
---------------------------------

.. _debops.ntp v0.2.2: https://github.com/debops/ansible-ntp/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Remove the ``ntp`` package before installing the ``openntpd`` package to
  avoid issues with AppArmor profiles. [thiagotalma]

- Use the ``timedatectl`` command to set the timezone on systems with
  ``systemd-timesyncd`` enabled. [thiagotalma]

- Update documentation and Changelog. [drybjed]

- Use different NTP server pools for Debian and ubuntu distributions. [drybjed]


`debops.ntp v0.2.1`_ - 2016-05-19
---------------------------------

.. _debops.ntp v0.2.1: https://github.com/debops/ansible-ntp/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Completed namespace change to ``ntp__`` from v0.2.0. [ypid]


`debops.ntp v0.2.0`_ - 2016-05-19
---------------------------------

.. _debops.ntp v0.2.0: https://github.com/debops/ansible-ntp/compare/v0.1.0...v0.2.0

Added
~~~~~

- Support configuration of ``openntpd`` startup options. This is needed to add
  the ``-s`` flag so that the daemon will synchronize time immediately on
  startup if the difference is large enough. [drybjed]

- Add support for ``system-timesyncd`` configuration. If other daemons are
  enabled, role will automatically disable the ``system-timesyncd`` service so
  that it won't interfere with normal operations. [drybjed]

Changed
~~~~~~~

- The ``tzdata`` package is frequently updated after the Debian Stable release
  and almost always newer version will be available from ``stable-updates``
  repository. This results in frequent e-mail messages informing about updated
  ``tzdata`` package available to install. This change ensures that on first
  configuration of a host, ``tzdata`` package will be updated automatically,
  which should help ensure that mentioned e-mails won't be sent. [drybjed]

- Configure ``/etc/timezone`` using template.

  In Ansible v2, using ``copy`` module with ``content`` parameter is
  unreliable, since the "end of line" character is rendered directly in the
  file. Switching to ``template`` module ensures that generated configuration
  file has correct formatting and should stop generating idempotency issues
  with ``tzdata`` package configuration. [drybjed]

- Check if NTP daemon can be installed in Ansible facts. [drybjed]

- Changed variable namespace from ``ntp_`` to ``ntp__``.
  ``ntp_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(ntp)_([^_])/\1__\2/g;'

  [drybjed]

- Update documentation. [drybjed]


debops.ntp v0.1.0 - 2015-11-13
------------------------------

Added
~~~~~

- Add Changelog [drybjed]

- Added support for ``ntpdate``. [ypid]

Changed
~~~~~~~

- Uninstall conflicting packages before installing the requested ones. This
  should fix `ntp and AppArmor issue`_ present in Ubuntu. [drybjed]

.. _ntp and Apparmor issue: https://bugs.launchpad.net/ubuntu/+source/openntpd/+bug/458061

- Fixed ``ntp_listen: '*'`` for NTPd. [ypid]

- Rewrite the installation tasks to work correctly on Ansible v2. [drybjed]

- Drop the dependency on ``debops.ferm`` Ansible role, firewall configuration
  is now defined in role default variables, and can be used by other roles
  through playbooks. [drybjed]
