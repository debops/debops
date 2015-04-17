Changelog
=========

v0.1.2
------

*Unreleased*

- Add DebOps pre/post task hooks using ``task_src`` lookup. [drybjed]

- Add ``users-dotfiles`` Ansible tag for tasks related to dotfiles. [drybjed]

- Don't force certain ``user`` module parameters if they are not specified by
  the user, like the account ``system`` state or home directory location. This
  should avoid problems with accounts that weren't defined with default values
  and are now managed by Ansible. [drybjed]

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

