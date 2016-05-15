Changelog
=========

v0.2.1
------

*Unreleased*

- Added ``preseed_dependencies`` to allow to disable role dependencies. [ypid]

- Fix deprecation warnings in Ansible 2.1.0. [ypid]

- Changed variable namespace from ``preseed_`` to ``preseed__``.
  ``preseed_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(preseed)_([^_])/\1__\2/g;'

  [ypid]

v0.2.0
------

*Released: 2015-09-06*

- Add variables to set admin account home directory group and permissions.
  Admin account will be created and managed only if it doesn't exist. [drybjed]

- Change the SSH public key lookup to not cause issues when :command:`ssh-add` does
  not return any keys. Thanks, xorgic! [drybjed]

- Reworked documentation. [ypid]

- keymap can now be preseeded using ``item.keyboard_keymap`` or ``preseed_debian_keyboard_keymap``. [ypid]

- Made more preseed options configurable via Ansible. [ypid]

- Removed not-working preseed options. [ypid]

- Made APT proxy configurable via ``preseed_debian_mirror_proxy``. [ypid]

v0.1.1
------

*Released: 2015-05-01*

- Add ``resolvconf`` to list of packages installed by default. Debian Installer
  installs ``rdnssd`` if IPv6 network is detected which overrides
  :file:`/etc/resolv.conf` if the former package is not installed. Adding
  ``resolvconf`` prevents loss of configuration like IPv4 nameservers and
  domain/search options. [drybjed]

- Add ``grub-installer`` Jinja block in the preseed templates. The destructive
  template will automatically install ``grub`` on a default partition on new
  Jessie installs. [drybjed]

- Switch from using one admin group to adding the admin account to multiple
  system groups, which will be created if necessary. [drybjed]

- Allow configuration of a system group which will be configured with
  passwordless ``sudo`` access. By default it will be first group defined in
  ``preseed_admin_groups`` list. [drybjed]

v0.1.0
------

*Released: 2015-04-12*

- Initial release [drybjed]

