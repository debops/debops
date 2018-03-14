.. _changelog:

Changelog
=========

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

This file contains only general overview of the changes in the DebOps project.
The detailed changelog can be seen using :command:`git log` command.

You can read information about required changes between releases in the
:ref:`upgrade_notes` documentation.


`debops master`_ - unreleased
-----------------------------

.. _debops master: https://github.com/debops/debops/compare/v0.7.0...master

Added
~~~~~

- New DebOps roles:

  - :ref:`debops.apt_mark`: set install state of APT packages (manual/auto) or
    specify that particular packages should be held in their current state.
    The role is included in the ``common.yml`` playbook.

Changed
~~~~~~~

- [debops.lxc] The role will now generate the ``lxc-debops`` LXC template
  script from different templates, based on an OS release. This change should
  help fix the issues with LXC container creation on Debian Stretch.

- The test suite used on Travis-CI now checks the syntax of the YAML files, as
  well as Python and shell scripts included in the repository. The syntax is
  checked using the :command:`yamllint`, :command:`pycodestyle` and
  :command:`shellcheck` scripts, respectively. Tests can also be invoked
  separately via the :command:`make` command.

- [debops.etherpad] The role can now autodetect and use a PostgreSQL database
  as a backend database for Etherpad.

Fixed
~~~~~

- The :command:`debops` command will now generate the :file:`ansible.cfg`
  configuration file with correct path to the Ansible roles provided with the
  DebOps Python package.

- [debops.nginx] Fix a long standing bug in the role with Ansible failing
  during welcome page template generation with Jinja2 >= 2.9.4. It was related
  to `non-backwards compatible change in Jinja`__ that modified how variables
  are processed in a loop.

.. __: https://github.com/pallets/jinja/issues/659


`debops v0.7.0`_ - 2018-02-11
-----------------------------

.. _debops v0.7.0: https://github.com/debops/debops/compare/v0.6.0...v0.7.0

Added
~~~~~

- New Ansible roles have been imported from the ``debops-contrib``
  organization: ``apparmor``, ``bitcoind``, ``btrfs``, ``dropbear_initramfs``,
  ``etckeeper``, ``firejail``, ``foodsoft``, ``fuse``, ``homeassistant``,
  ``kernel_module``, ``kodi``, ``neurodebian``, ``snapshot_snapper``, ``tor``,
  ``volkszaehler``, ``x2go_server``. They are not yet included in the main
  playbook and still need to be renamed to fit with the rest of the
  ``debops.*`` roles.

- New DebOps roles:

  - :ref:`debops.sysfs`: configuration of the Linux kernel attributes through
    the :file:`/sys` filesystem. The role is not enabled by default.

  - :ref:`debops.locales`: configure localization and internationalization on
    a given host or set of hosts.

  - :ref:`debops.machine`: manage the :file:`/etc/machine-info` file,
    the :file:`/etc/issue` file and a dynamic MOTD.

  - :ref:`debops.proc_hidepid`: configure the ``/proc`` ``hidepid=`` options.

  - :ref:`debops.roundcube`: manage RoundCube Webmail application

  - :ref:`debops.prosody`: configure an xmpp server on a given host

  - :ref:`debops.sysnews`: manage System News bulletin for UNIX accounts

- You can now :ref:`use Vagrant <quick_start__vagrant>` to create an Ansible
  Controller based on Debian Stretch and use it to manage itself or other hosts
  over the network.

- You can now build an Ansible Controller with DebOps support as a Docker
  container. :ref:`Official Docker image <quick_start__docker>` is also
  available, automatically rebuilt on every commit.

- You can now install DebOps on `Arch Linux <https://www.archlinux.org/>`__
  using an included ``PKGBUILD`` file.

- Add new playbook, ``agent.yml``. This playbook is executed at the end of the
  main playbook, and contains applications or services which act as "agents" of
  other services. They may contact their parent applications to report about
  the state of the host they are executed on, therefore the agents are
  installed and configured at the end of the main playbook.

- [debops.libvirtd] The role can now detect if nested KVM is enabled in
  a particular virtual machine and install KVM support.

  [debops.nodejs] The :ref:`debops.nodejs` role can now install `Yarn
  <https://yarnpkg.com/>`_ package manager using its upstream APT repository
  (not enabled by default).

- DebOps roles and playbooks can now be tested using local or remote
  `GitLab CI <https://about.gitlab.com/>`_ instance, with Vagrant, KVM and LXC
  technologies and some custom scripts.

- DebOps roles and playbooks will be included in the Python packages released
  on PyPI. This will allow for easier installation of DebOps via :command:`pip`
  (no need to download the roles and playbooks separately) as well as simple
  stable releases. The DebOps monorepo can still be installed separately.

Changed
~~~~~~~

- [debops-tools] The :command:`debops-update` script will now install or
  update the DebOps monorepo instead of separate ``debops-playbooks`` and
  DebOps roles git repositories. Existing installations shouldn't be affected.

- [debops-tools] The :command:`debops` script will now include the DebOps
  monorepo roles and playbooks in the generated :file:`ansible.cfg`
  configuration. The monorepo roles and playbooks are preferred over the old
  ``debops-playbooks`` ones.

  The script is backwards compatible and should work correctly with or without
  the ``debops-playbooks`` repository and roles installed.

- The project repository is tested using :command:`pycodestyle` for compliance
  with Python's `PEP8 Style Guide <https://pep8.org/>`_.

- [debops.nodejs] The ``npm`` package has been removed from Debian Stable.
  The role will now install NPM using the GitHub source, unless upstream NodeJS is
  enabled, which includes its own NPM version.

- [debops.gunicorn] Update the role to work correctly on Debian Stretch and
  newer releases. The support for multiple :command:`gunicorn` instances using
  custom Debian scripts has been removed in Debian Stretch, therefore the role
  replaces it with its own setup based on :command:`systemd` instances.

- [debops.gitlab_runner] The GitLab Runner playbook is moved to the
  ``agent.yml`` playbook; it will be executed at the end of the main playbook
  and should that way include correct information about installed services.

- Improved Python 3 support in the DebOps scripts and throughout the
  playbooks/roles. DebOps should now be compatible with both Python versions.

Removed
~~~~~~~

- [DebOps playbooks] Remove the :file:`ipaddr.py` Ansible filter plugin, it is
  now included in the Ansible core distribution.

- [debops.console] Remove the ``locales`` configuration from the
  'debops.console' role, this functionality has been moved to the new
  'debops.locales' role. You will need to update the Ansible inventory
  variables to reflect the changes.

- [debops.console] Remove management of the :file:`/etc/issue` and
  :file:`/etc/motd` files from the ``debops.console`` role. That functionality
  is now available in the :ref:`debops.machine` role. You will need to update
  the Ansible inventory variables to reflect the changes.

- [debops.console] Management of the ``/proc`` ``hidepid=`` option has been
  moved to a new role, :ref:`debops.proc_hidepid`. You will need to update the
  Ansible inventory variables to reflect the changes.

- [debops.console] Management of the System News using the ``sysnews`` Debian
  package has been removed from the role; it's now available as a separate
  :ref:`debops.sysnews` Ansible role. You will need to update the Ansible
  inventory variables related to System News due to this changes.


debops v0.6.0 - 2017-10-21
--------------------------

Added
~~~~~

- Various repositories that comprise the DebOps project have been merged into
  a single monorepo which will be used as the main development repository.
  Check the :command:`git` log for information about older releases of DebOps
  roles and/or playbooks.
