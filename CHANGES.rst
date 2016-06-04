Changelog
=========

v0.2.2
------

*Unreleased*

- Explicitly set ``!requiretty`` for the :any:`bootstrap__sudo_group`
  (:manpage:`sudoers(5)`). This ensures that ``sudo`` with ``rsync`` is allowed
  for the :any:`bootstrap__sudo_group` even when ``requiretty`` has been
  configured to be the default for users.

v0.2.1
------

*Released: 2016-05-28*

- Small fixes and documentation updates. [drybjed]

v0.2.0
------

*Released: 2016-05-07*

- Fixed incorrectly evaluated ``bootstrap_admin_system`` variable since "Clean
  up task logic" in v0.1.2. [ypid]

- Reworked tasks and conditions. [ypid]

- Added ``role::bootstrap:packages`` and ``role::bootstrap:admin`` tags. [ypid]

- Changed variable namespace from ``bootstrap_`` to ``bootstrap__``.
  ``bootstrap_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(bootstrap)_([^_])/\1__\2/g;'

  [ypid]

v0.1.2
------

*Released: 2016-02-08*

- Preserve existing DNS domain if any has been detected by Ansible. This solves
  an issue where an existing domain is removed from a host when
  ``bootstrap_domain`` is not defined in inventory. [drybjed]

- Change the way ``ansible_ssh_user`` variable is detected. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Clean up task logic. [drybjed]

- Change the hostname only when current one differs. [drybjed]

v0.1.1
------

*Released: 2015-11-07*

- Update the task list so that correct hostname is set in ``/etc/hosts`` even
  when ``bootstrap_domain`` is not specified. [drybjed]

- Added a IPv6 entry to ``/etc/hosts`` for the FQDN of the host pointing to the
  IPv6 loopback address "::1". Not enabled by default because it might break something.
  Can be enabled by setting ``bootstrap_hostname_v6_loopback`` to True. [ypid]

- Don't try and set SSH public key on ``root`` account when admin account
  management is disabled. [drybjed]

- Remove the "\n" from ``/etc/hostname`` content line to prevent issues on
  Ansible v2. [drybjed]

- Replace the quotes in ``lineinfile`` module to prevent issues with ``\t``
  characters on Ansible v2. [drybjed]

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed]

v0.1.0
------

*Released: 2015-07-14*

- Initial release. [drybjed]

