Changelog
=========

v0.1.2
------

*Released: 2016-02-08*

- Preserve existing DNS domain if any has been detected by Ansible. This solves
  an issue where an existing domain is removed from a host when
  ``bootstrap_domain`` is not defined in inventory. [drybjed]

- Change the way ``ansible_ssh_user`` variable is detected. [drybjed]

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

