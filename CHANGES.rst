Changelog
=========

v0.2.0
------

*Unreleased*

- Remove most of the Ansible role dependencies, leaving only those that are
  required for the role to run correctly.

  Configuration of dependent services like firewall, TCP Wrappers, APT
  preferences is set in separate default variables. These variables can be used
  by Ansible playbooks to configure settings related to :program:`libvirtd` in other
  services. [ypid]

- Fix deprecation warnings in Ansible 2.1.0. [ypid]

- Fix issue with wrong variable type conversion. [drybjed]

- Changed variable namespace from ``libvirtd_`` to ``libvirtd__``.
  ``libvirtd_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(libvirtd)_([^_])/\1__\2/g;'

  [ypid]

v0.1.2
------

*Released: 2015-11-12*

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed]

v0.1.1
------

*Released: 2015-07-27*

- Fix documentation formatting. [drybjed]

v0.1.0
------

*Released: 2015-07-27*

- Initial release. [drybjed]

