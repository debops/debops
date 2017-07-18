Changelog
=========

.. include:: includes/all.rst

**debops.sysctl**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is ypid_.


`debops.sysctl master`_ - unreleased
------------------------------------

.. _debops.sysctl master: https://github.com/debops/ansible-sysctl/compare/v0.1.0...master

Added
~~~~~

- Add :envvar:`sysctl__swappiness` and :envvar:`sysctl__vfs_cache_pressure` which where
  previously handled by debops.swapfile_ under similar names. [ypid_]


Fixed
~~~~~

- Don't set ``net.ipv4.tcp_rfc1337`` and ``net.ipv4.tcp_timestamps`` keys in
  OpenVZ containers, it isn't allowed. [pedroluislopez_]

- Make sure that role works in Ansible ``--check`` mode. [drybjed_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Don't configure paging on LXC guest containers, it isn't allowed. [pedroluislopez_]


debops.sysctl v0.1.0 - 2016-09-04
---------------------------------

Added
~~~~~

- Moved sysctl parts from debops.console_ to the separate ``debops.sysctl``
  role. [ypid_]

- Ignore errors about unknown kernel parameters when ``cap_sys_admin`` is not
  in the Linux capability list to allow to configure container with the role.
  [ypid_]

- Instead of using the :command:`sysctl` Ansible module directly for each parameter,
  role will now generate the :command:`sysctl` configuration file using a template and
  apply all of the configuration at once, including the kernel parameters from
  other :command:`sysctl` configuration files (when supported). This makes the role
  faster and less prone to issues with missing kernel parameters. [drybjed_]
