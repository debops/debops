Changelog
=========

v0.1.4
------

*Released: 2016-02-08*

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Add a note about IP addresses of Ansible Controller and ``become`` setting in
  inventory. [drybjed]

v0.1.3
------

*Released: 2015-12-17*

- Gather local facts if they changed, in case the role is used in a play with
  other roles. [drybjed]

v0.1.2
------

*Released: 2015-10-19*

- Add a ``core_active_controller`` variable which specifies IP address of
  active Ansible Controller. [drybjed]

v0.1.1
------

*Released: 2015-08-22*

- Add script to gather information from ``/etc/resolv.conf``, available in the
  Ansible Facts as ``ansible_local.resolver.*``. [drybjed]

v0.1.0
------

*Released: 2015-08-22*

- Initial release. [drybjed]

