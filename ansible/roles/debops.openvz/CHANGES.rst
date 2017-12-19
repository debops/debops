Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Move OpenVZ repository variables from ``vars/main.yml`` to
  ``defaults/main.yml`` so that they can be overridden if necessary. [drybjed]

- Expand admin account variables to allow for system admin accounts with more
  configuration options like default shell, multiple system groups, different
  location of home directories. [drybjed]

- Change how bootstrap script detects that container is already bootstrapped.
  [drybjed]

- Add option to disable kernel configuration. [drybjed]

- Add variables to set admin account home directory group and permissions.
  Admin account will be created only when not already present.
  [drybjed]

- Change the SSH public key lookup to not cause problems with ``ssh-add`` does
  not return any keys. Thanks, xorgic! [drybjed]

