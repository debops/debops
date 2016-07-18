Changelog
=========

**debops.bootstrap**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.bootstrap master`_ - unreleased
---------------------------------------

.. _debops.bootstrap master: https://github.com/debops/ansible-bootstrap/compare/v0.2.2...master


`debops.bootstrap v0.2.2`_ - 2016-07-18
---------------------------------------

.. _debops.bootstrap v0.2.2: https://github.com/debops/ansible-bootstrap/compare/v0.2.1...v0.2.2

Added
~~~~~

- Allow to disable hostname and domain configuration via
  :any:`bootstrap__hostname_domain_config_enabled`. [ypid]

Changed
~~~~~~~

- Explicitly set ``!requiretty`` for the :any:`bootstrap__sudo_group`
  (:manpage:`sudoers(5)`). This ensures that :command:`sudo` with :command:`rsync` is allowed
  for the :any:`bootstrap__sudo_group` even when ``requiretty`` has been
  configured to be the default for users. [ypid]

- Split the role into two roles, ``debops.bootstrap/raw`` and
  ``debops.bootstrap``. This allows use of separate plays for each role, the
  first one without any ``environment`` variables, the second one that works
  normally. [drybjed]

- Update documentation and Changelog. [drybjed]


`debops.bootstrap v0.2.1`_ - 2016-05-28
---------------------------------------

.. _debops.bootstrap v0.2.1: https://github.com/debops/ansible-bootstrap/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Small fixes and documentation updates. [drybjed]


`debops.bootstrap v0.2.0`_ - 2016-05-07
---------------------------------------

.. _debops.bootstrap v0.2.0: https://github.com/debops/ansible-bootstrap/compare/v0.1.2...v0.2.0

Added
~~~~~

- Added ``role::bootstrap:packages`` and ``role::bootstrap:admin`` tags. [ypid]

Changed
~~~~~~~

- Reworked tasks and conditions. [ypid]

- Changed variable namespace from ``bootstrap_`` to ``bootstrap__``.
  ``bootstrap_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(bootstrap)_([^_])/\1__\2/g;'

  [ypid]

Fixed
~~~~~

- Fixed incorrectly evaluated ``bootstrap_admin_system`` variable since "Clean
  up task logic" in v0.1.2. [ypid]


`debops.bootstrap v0.1.2`_ - 2016-02-08
---------------------------------------

.. _debops.bootstrap v0.1.2: https://github.com/debops/ansible-bootstrap/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Preserve existing DNS domain if any has been detected by Ansible. This solves
  an issue where an existing domain is removed from a host when
  ``bootstrap_domain`` is not defined in inventory. [drybjed]

- Change the way ``ansible_ssh_user`` variable is detected. [drybjed]

- Clean up task logic. [drybjed]

- Change the hostname only when current one differs. [drybjed]

Fixed
~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]


`debops.bootstrap v0.1.1`_ - 2015-11-07
---------------------------------------

.. _debops.bootstrap v0.1.1: https://github.com/debops/ansible-bootstrap/compare/v0.1.0...v0.1.1

Added
~~~~~

- Added a IPv6 entry to :file:`/etc/hosts` for the FQDN of the host pointing to the
  IPv6 loopback address "::1". Not enabled by default because it might break something.
  Can be enabled by setting ``bootstrap_hostname_v6_loopback`` to True. [ypid]

Changed
~~~~~~~

- Update the task list so that correct hostname is set in :file:`/etc/hosts` even
  when ``bootstrap_domain`` is not specified. [drybjed]

- Don't try and set SSH public key on ``root`` account when admin account
  management is disabled. [drybjed]

- Replace the quotes in ``lineinfile`` module to prevent issues with ``\t``
  characters on Ansible v2. [drybjed]

Fixed
~~~~~

- Remove the "\n" from :file:`/etc/hostname` content line to prevent issues on
  Ansible v2. [drybjed]

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed]


debops.bootstrap v0.1.0 - 2015-07-14
------------------------------------

Added
~~~~~

- Initial release. [drybjed]
