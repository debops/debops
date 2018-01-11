.. _users__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.users**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.users master`_ - unreleased
-----------------------------------

.. _debops.users master: https://github.com/debops/ansible-users/compare/v0.2.1...master

Added
~~~~~

- Added new variables :envvar:`users__dependent_accounts` and
  :envvar:`users__dependent_groups` making the role usable for other roles
  which require more sophisticated user account setups. [ganto_]

Changed
~~~~~~~

- Omit ``group`` parameter of :envvar:`users__accounts` by default.
  Previously, it was set to username by default. [tootoonchian_]


`debops.users v0.2.1`_ - 2016-10-16
-----------------------------------

.. _debops.users v0.2.1: https://github.com/debops/ansible-users/compare/v0.2.0...v0.2.1

Added
~~~~~

- Allow creation of user accounts with non-unique UID numbers. [kosma]


`debops.users v0.2.0`_ - 2016-10-13
-----------------------------------

.. _debops.users v0.2.0: https://github.com/debops/ansible-users/compare/v0.1.6...v0.2.0

Added
~~~~~

- Disable Ansible logging for all tasks in the role that work with user account
  lists to prevent accidental password leaks. This can be controlled by
  a default variable to make debugging easier. [drybjed_]

- Add support for custom resource management in user directories (files,
  directories, symlinks). [drybjed_]

Changed
~~~~~~~

- Updated documentation and Changelog. [drybjed_]

- All variables are renamed from ``users_*`` to ``users__*`` to put them in
  a separate namespace. [drybjed_]

- Rename user account and group lists to make them more organized. [drybjed_]

- Use the list of admin users maintained by the debops.core_ Ansible facts to
  manage the administrator accounts. [drybjed_]

- Switch from using a template for :file:`~/.forward` file to the Ansible
  ``lineinfile`` module. [drybjed_]

- Reorganize the user configuration file management, including better control
  over where dotfiles are cloned, and easier way to add new dotfiles
  definitions via a separate YAML dictionary. Some of the variables related to
  dotfiles have been renamed. [drybjed_]

- A default shell can now be set for all user accounts managed by this role, by
  setting it in the :envvar:`users__default_shell` variable. [drybjed_]

- Update the tasks that manage SSH public keys. You can specify the ``sshkeys``
  parameter as a string or a list, set the specified keys as exclusive or
  entirely remove the ``~/.ssh/authorized_keys`` file. [drybjed_]

Removed
~~~~~~~

- Remove the ``users__default_groups_list`` and
  ``users__default_groups_append`` variables, as well as the task that utilized
  these variables. [drybjed_]

Fixed
~~~~~

- Allow removal of user groups only if ``item.group`` parameter is the same as
  ``item.name`` or is not specified. This fixes an issue where Ansible tried to
  remove a group which was a primary group for multiple users. [drybjed_]


`debops.users v0.1.6`_ - 2016-02-06
-----------------------------------

.. _debops.users v0.1.6: https://github.com/debops/ansible-users/compare/v0.1.5...v0.1.6

Added
~~~~~

- Enable support for SSH key management on ``root`` account. [drybjed_]

- Add more useful parameters to user management. [drybjed_]

Changed
~~~~~~~

- Rename the ``users`` variable to ``users_enabled`` to avoid the issue with
  single-word variables. You might need to update the Ansible inventory.
  [drybjed_]

- Change the method that role detects and uses ``ansible_ssh_user`` variable to
  set up default user account. [drybjed_]

- Switch ``sudo_user`` to ``become_user``. [drybjed_]

- Fix Ansible 2.1.0 deprecation warnings. [drybjed_]


`debops.users v0.1.5`_ - 2016-01-05
-----------------------------------

.. _debops.users v0.1.5: https://github.com/debops/ansible-users/compare/v0.1.4...v0.1.5

Added
~~~~~

- Add ``users_default_system`` bool variable which, when enabled, will set all
  user groups and accounts created by ``debops.users`` role as "system"
  accounts with UID/GID < 1000. These accounts are considered "local" accounts
  and should not interfere with LDAP accounts. This can still be overridden by
  explicitly setting ``item.system`` parameter in user account definition.
  [drybjed_]

- Add dependency on debops.secret_ role which can be accessed by
  ``debops.users``, for example to retrieve SSH keys. This ensures that the
  required ``secret`` variable is always present. [drybjed_]

Changed
~~~~~~~

- Fix empty list of default users on Ansible v2. [drybjed_]

Removed
~~~~~~~

- Remove unneeded bracket. [sean]


`debops.users v0.1.4`_ - 2015-08-22
-----------------------------------

.. _debops.users v0.1.4: https://github.com/debops/ansible-users/compare/v0.1.3...v0.1.4

Changed
~~~~~~~

- Get list of available groups even in Ansible check mode to avoid error. [ypid_]

- Request :command:`sudo` access on Travis-CI for testing. [drybjed_]


`debops.users v0.1.3`_ - 2015-08-22
-----------------------------------

.. _debops.users v0.1.3: https://github.com/debops/ansible-users/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add ``item.home_owner`` parameter which allows to change the owner of the
  home directory if needed. [drybjed_]

Changed
~~~~~~~

- Check if ``item.createhome`` is specified or not for an account before doing
  anything within the home directory. If home creation is disabled,
  configuration of ``~/.forward`` file and dotfiles won't be performed.
  [drybjed_]

Removed
~~~~~~~

- Remove support for ``root`` account management; this functionality has been
  moved to debops.console_ role. Management of the dotfiles on ``root``
  account is still done from this role. [drybjed_]


`debops.users v0.1.2`_ - 2015-08-22
-----------------------------------

.. _debops.users v0.1.2: https://github.com/debops/ansible-users/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add DebOps pre/post task hooks using ``task_src`` lookup. [drybjed_]

- Add ``users-dotfiles`` Ansible tag for tasks related to dotfiles. [drybjed_]

- Add a way to change home directory primary group and permissions using
  ``item.home_group`` and ``item.home_mode`` parameters. [drybjed_]

- Add user accounts only to groups that already exist. [drybjed_]

Changed
~~~~~~~

- Don't force certain ``user`` module parameters if they are not specified by
  the user, like the account ``system`` state or home directory location. This
  should avoid problems with accounts that weren't defined with default values
  and are now managed by Ansible. [drybjed_]

- Set user shell separately if dotfiles are enabled and it's specified in the
  dotfiles dict. [drybjed_]

- Don't change ``root`` shell if none is specified by the user. [drybjed_]

- Don't manage default account if it's ``root``, it should fix problems when
  ``root`` account is used over SSH directly. [drybjed_]

- Use ``sudo_user`` task parameter to operate on files inside user directories
  instead of relying on static absolute paths as default. [drybjed_]

- Rename the ``item.systemgroup`` and ``item.systemuser`` parameters to
  ``item.system`` and omit them if not specified (system status won't be
  enforced by the role). [drybjed_]

- Allow home group and mode modification without specifying the ``item.home``
  key. [drybjed_]

- Default user account will be added to ``admins`` group to fix an issue where
  if that account is added manually, it loses access to :command:`sudo` commands.
  [drybjed_]

- Small update of the example user entry to correctly show how a separate Jinja
  dictionary can be passed to a list of user accounts. [drybjed_]


`debops.users v0.1.1`_ - 2015-02-25
-----------------------------------

.. _debops.users v0.1.1: https://github.com/debops/ansible-users/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add CHANGES.rst [drybjed_]

Changed
~~~~~~~

- Role will now correctly remove user accounts when requested. You can also
  optionally remove user's home directory. [drybjed_]

- You can optionally disable home creation and set account expiration date.
  [drybjed_]


debops.users v0.1.0 - 2015-02-09
--------------------------------

Added
~~~~~

- First release. [drybjed_]
