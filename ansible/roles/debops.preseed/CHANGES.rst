Changelog
=========

.. include:: includes/all.rst

v0.3.0
------

*Released: 2016-05-28*

- Added ``preseed_dependencies`` to allow to disable role dependencies. [ypid_]

- Fix deprecation warnings in Ansible 2.1.0. [ypid_]

- Changed variable namespace from ``preseed_`` to ``preseed__``.
  ``preseed_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(preseed)_([^_])/\1__\2/g;'

  [ypid_]

- Remove most of the Ansible role dependencies, leaving only those that are
  required for the role to run correctly.

  Configuration of dependent services like :program:`nginx` is set in separate default
  variables. These variables can be used by Ansible playbooks to configure
  settings related to ``preseed`` in other services. [ypid_]

- Removed ``preseed_dependencies`` variable. This can now be handled on the
  playbook level. [ypid_]

- Switched the default Debian mirror to the new official redirector at
  http://httpredir.debian.org/. [ypid_]

- Divert original :file:`/etc/default/grub` away before making changes to it. [ypid_]

- Made GRUB settings configurable. [ypid_]

- Don’t configure ``GRUB_DISABLE_RECOVERY="true"`` in :file:`/etc/default/grub` anymore.
  This option should be handled by debops.grub_. [ypid_]

- Don’t ask for additional installation media when the installer configures
  APT. This behavior can be changed via
  :envvar:`preseed__debian_ask_for_additional_install_media`.
  [ypid_]

- Reworked documentation. [ypid_]

- Removed deprecated hostgroup ``debops_preseed``, your hosts will now need to be
  in ``debops_service_preseed``. [ypid_]

v0.2.0
------

*Released: 2015-09-06*

- Add variables to set admin account home directory group and permissions.
  Admin account will be created and managed only if it doesn't exist. [drybjed_]

- Change the SSH public key lookup to not cause issues when :command:`ssh-add` does
  not return any keys. Thanks, xorgic! [drybjed_]

- Reworked documentation. [ypid_]

- keymap can now be preseeded using ``item.keyboard_keymap`` or ``preseed_debian_keyboard_keymap``. [ypid_]

- Made more preseed options configurable via Ansible. [ypid_]

- Removed not-working preseed options. [ypid_]

- Made APT proxy configurable via ``preseed_debian_mirror_proxy``. [ypid_]

v0.1.1
------

*Released: 2015-05-01*

- Add ``resolvconf`` to list of packages installed by default. Debian Installer
  installs ``rdnssd`` if IPv6 network is detected which overrides
  :file:`/etc/resolv.conf` if the former package is not installed. Adding
  ``resolvconf`` prevents loss of configuration like IPv4 nameservers and
  domain/search options. [drybjed_]

- Add ``grub-installer`` Jinja block in the preseed templates. The destructive
  template will automatically install ``grub`` on a default partition on new
  Jessie installs. [drybjed_]

- Switch from using one admin group to adding the admin account to multiple
  system groups, which will be created if necessary. [drybjed_]

- Allow configuration of a system group which will be configured with
  passwordless :command:`sudo` access. By default it will be first group defined in
  ``preseed_admin_groups`` list. [drybjed_]

v0.1.0
------

*Released: 2015-04-12*

- Initial release [drybjed_]
