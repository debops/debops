Changelog
=========

.. include:: includes/all.rst

**debops.bootstrap**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.bootstrap master`_ - unreleased
---------------------------------------

.. _debops.bootstrap master: https://github.com/debops/ansible-bootstrap/compare/v0.3.3...master


`debops.bootstrap v0.3.3`_ - 2017-01-19
---------------------------------------

.. _debops.bootstrap v0.3.3: https://github.com/debops/ansible-bootstrap/compare/v0.3.2...v0.3.3

Added
~~~~~

- Added support for Ansible 2.0 and higher where `ansible_ssh_user` is deprecated
  and replaced by `ansible_user`. [tallandtree_]

- Change the ``apt`` module to ``package`` to make the role more generic.
  [JeanVEGA]

- Use the ``inventory_hostname`` variable as a default source of the host's
  domain instead of ``ansible_domain`` variable. [drybjed_]


`debops.bootstrap v0.3.2`_ - 2016-09-13
---------------------------------------

.. _debops.bootstrap v0.3.2: https://github.com/debops/ansible-bootstrap/compare/v0.3.1...v0.3.2

Fixed
~~~~~

- Fix an issue where disabled admin account management resulted in an error.
  Now, ``getent`` database is always checked, therefore other tasks can be
  correctly skipped by Ansible. [drybjed_]


`debops.bootstrap v0.3.1`_ - 2016-08-14
---------------------------------------

.. _debops.bootstrap v0.3.1: https://github.com/debops/ansible-bootstrap/compare/v0.3.0...v0.3.1

Fixed
~~~~~

- Potential issue when :envvar:`bootstrap__admin_default_users` and
  :envvar:`bootstrap__admin_users` would both be empty. [ypid_]


`debops.bootstrap v0.3.0`_ - 2016-08-13
---------------------------------------

.. _debops.bootstrap v0.3.0: https://github.com/debops/ansible-bootstrap/compare/v0.2.2...v0.3.0

Changed
~~~~~~~

- Role now supports creation and management of multiple admin accounts. See
  :ref:`bootstrap__ref_admin_users` for more details. [drybjed_]

- Role now requires Ansible v2.0.0 to work properly. [drybjed_]

- The ``bootstrap__admin_system_home`` variable has been renamed to
  :envvar:`bootstrap__admin_home_path_system` due to changes in admin account
  support. [drybjed_]

- The admin accounts will be added to the :command:`sudo` system group by default.
  [drybjed_]

Removed
~~~~~~~

- The ``bootstrap__admin_name`` variable has been removed due to changes in
  admin account support. [drybjed_]

- The ``bootstrap__admin_manage_existing`` variable has been removed due to
  changes in admin account support. Role now detects existing account
  parameters and preserves them unless configured specifically to change them.
  [drybjed_]


`debops.bootstrap v0.2.2`_ - 2016-07-18
---------------------------------------

.. _debops.bootstrap v0.2.2: https://github.com/debops/ansible-bootstrap/compare/v0.2.1...v0.2.2

Added
~~~~~

- Allow to disable hostname and domain configuration via
  :envvar:`bootstrap__hostname_domain_config_enabled`. [ypid_]

Changed
~~~~~~~

- Explicitly set ``!requiretty`` for the :envvar:`bootstrap__sudo_group`
  (:manpage:`sudoers(5)`). This ensures that :command:`sudo` with :command:`rsync` is allowed
  for the :envvar:`bootstrap__sudo_group` even when ``requiretty`` has been
  configured to be the default for users. [ypid_]

- Split the role into two roles, ``debops.bootstrap/raw`` and
  ``debops.bootstrap``. This allows use of separate plays for each role, the
  first one without any ``environment`` variables, the second one that works
  normally. [drybjed_]

- Update documentation and Changelog. [drybjed_]

- Move the conditional check for POSIX capabilities to default variables.
  [drybjed_]


`debops.bootstrap v0.2.1`_ - 2016-05-28
---------------------------------------

.. _debops.bootstrap v0.2.1: https://github.com/debops/ansible-bootstrap/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Small fixes and documentation updates. [drybjed_]


`debops.bootstrap v0.2.0`_ - 2016-05-07
---------------------------------------

.. _debops.bootstrap v0.2.0: https://github.com/debops/ansible-bootstrap/compare/v0.1.2...v0.2.0

Added
~~~~~

- Added ``role::bootstrap:packages`` and ``role::bootstrap:admin`` tags. [ypid_]

Changed
~~~~~~~

- Reworked tasks and conditions. [ypid_]

- Changed variable namespace from ``bootstrap_`` to ``bootstrap__``.
  ``bootstrap_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(bootstrap)_([^_])/\1__\2/g;'

  [ypid_]

Fixed
~~~~~

- Fixed incorrectly evaluated ``bootstrap_admin_system`` variable since "Clean
  up task logic" in v0.1.2. [ypid_]


`debops.bootstrap v0.1.2`_ - 2016-02-08
---------------------------------------

.. _debops.bootstrap v0.1.2: https://github.com/debops/ansible-bootstrap/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Preserve existing DNS domain if any has been detected by Ansible. This solves
  an issue where an existing domain is removed from a host when
  ``bootstrap_domain`` is not defined in inventory. [drybjed_]

- Change the way ``ansible_ssh_user`` variable is detected. [drybjed_]

- Clean up task logic. [drybjed_]

- Change the hostname only when current one differs. [drybjed_]

Fixed
~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [drybjed_]


`debops.bootstrap v0.1.1`_ - 2015-11-07
---------------------------------------

.. _debops.bootstrap v0.1.1: https://github.com/debops/ansible-bootstrap/compare/v0.1.0...v0.1.1

Added
~~~~~

- Added a IPv6 entry to :file:`/etc/hosts` for the FQDN of the host pointing to the
  IPv6 loopback address "::1". Not enabled by default because it might break something.
  Can be enabled by setting ``bootstrap_hostname_v6_loopback`` to True. [ypid_]

Changed
~~~~~~~

- Update the task list so that correct hostname is set in :file:`/etc/hosts` even
  when ``bootstrap_domain`` is not specified. [drybjed_]

- Don't try and set SSH public key on ``root`` account when admin account
  management is disabled. [drybjed_]

- Replace the quotes in ``lineinfile`` module to prevent issues with ``\t``
  characters on Ansible v2. [drybjed_]

Fixed
~~~~~

- Remove the "\n" from :file:`/etc/hostname` content line to prevent issues on
  Ansible v2. [drybjed_]

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed_]


debops.bootstrap v0.1.0 - 2015-07-14
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
