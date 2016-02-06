Changelog
=========

v0.1.6
------

*Released: 2016-02-06*

- Rename the ``users`` variable to ``users_enabled`` to avoid the issue with
  single-word variables. You might need to update the Ansible inventory.
  [drybjed]

- Change the method that role detects and uses ``ansible_ssh_user`` variable to
  set up default user account. [drybjed]

- Switch ``sudo_user`` to ``become_user``. [drybjed]

v0.1.5
------

*Released: 2016-01-05*

- Add ``users_default_system`` bool variable which, when enabled, will set all
  user groups and accounts created by ``debops.users`` role as "system"
  accounts with UID/GID < 1000. These accounts are considered "local" accounts
  and should not interfere with LDAP accounts. This can still be overriden by
  explicitly setting ``item.system`` parameter in user account definition.
  [drybjed]

- Fix empty list of default users on Ansible v2. [drybjed]

- Remove unneeded bracket. [sean]

- Add dependency on ``debops.secret`` role which can be accessed by
  ``debops.users``, for example to retrieve SSH keys. This ensures that the
  required ``secret`` variable is always present. [drybjed]

v0.1.4
------

*Released: 2015-08-22*

- Get list of available groups even in Ansible check mode to avoid error. [ypid]

- Request ``sudo`` access on Travis-CI for testing. [drybjed]

v0.1.3
------

*Released: 2015-08-22*

- Check if ``item.createhome`` is specified or not for an account before doing
  anything within the home directory. If home creation is disabled,
  configuration of ``~/.forward`` file and dotfiles won't be performed.
  [drybjed]

- Add ``item.home_owner`` parameter which allows to change the owner of the
  home directory if needed. [drybjed]

- Remove support for ``root`` account management; this functionality has been
  moved to ``debops.console`` role. Mmanagement of the dotfiles on ``root``
  account is still done from this role. [drybjed]

v0.1.2
------

*Released: 2015-08-22*

- Add DebOps pre/post task hooks using ``task_src`` lookup. [drybjed]

- Add ``users-dotfiles`` Ansible tag for tasks related to dotfiles. [drybjed]

- Don't force certain ``user`` module parameters if they are not specified by
  the user, like the account ``system`` state or home directory location. This
  should avoid problems with accounts that weren't defined with default values
  and are now managed by Ansible. [drybjed]

- Set user shell separately if dotfiles are enabled and it's specified in the
  dotfiles dict. [drybjed]

- Don't change ``root`` shell if none is specified by the user. [drybjed]

- Don't manage default account if it's ``root``, it should fix problems when
  ``root`` account is used over SSH directly. [drybjed]

- Use ``sudo_user`` task parameter to operate on files inside user directories
  instead of relying on static absolute paths as default. [drybjed]

- Rename the ``item.systemgroup`` and ``item.systemuser`` parameters to
  ``item.system`` and omit them if not specified (system status won't be
  enforced by the role). [drybjed]

- Add a way to change home directory primary group and permissions using
  ``item.home_group`` and ``item.home_mode`` parameters. [drybjed]

- Allow home group and mode modification without specifying the ``item.home``
  key. [drybjed]

- Add user accounts only to groups that already exist. [drybjed]

- Default user account will be added to ``admins`` group to fix an issue where
  if that account is added manually, it loses access to ``sudo`` commands.
  [drybjed]

- Small update of the example user entry to correctly show how a separate Jinja
  dictionary can be passed to a list of user accounts. [drybjed]

v0.1.1
------

*Released: 2015-02-25*

- Add CHANGES.rst [drybjed]

- Role will now correctly remove user accounts when requested. You can also
  optionally remove user's home directory. [drybjed]

- You can optionally disable home creation and set account expiration date.
  [drybjed]

v0.1.0
------

*Released: 2015-02-09*

- First release
  [drybjed]

