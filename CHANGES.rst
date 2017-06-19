Changelog
=========

`debops.lvm master`_ - unreleased
------------------------------------

.. _debops.lvm master: https://github.com/debops/ansible-lvm/compare/v0.1.5...master

- Added filesystem resize if logical volume is resized. [tallandtree]

- Updated documentation (hyphens supported in volume group name and resize
  filesystem). [tallandtree]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

v0.1.5
------

*Released: 2016-05-23*

- Sort configuration file sections to generate stable order of sections each
  time. This should fix an issue where consequent runs of ``debops.lvm`` role
  in the same Ansible playbook run re-generated the configuration file with
  different section order. [drybjed]

v0.1.4
------

*Released: 2016-05-19*

- Update documentation. [ypid]

- Compress Jinja statements. [ypid]

- Fix error with too many brackets. [drybjed]

v0.1.3
------

*Released: 2016-02-10*

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Update all role variables to use distinct namespace. [drybjed]

v0.1.2
------

*Released: 2015-10-27*

- Rewrite the :file:`/etc/lvm/lvm.conf` configuration. Instead of using
  ``lineinfile`` Ansible module to modify the original, use a normal template
  to generate the configuration from scratch using a base LVM configuration and
  modifying it by user variables. [drybjed]

- Remove DebOps hooks from the role, they are not needed here. [drybjed]

v0.1.1
------

*Released: 2015-07-16*

- Remove unnecessary comments from ``defaults/main.yml``. [drybjed]

v0.1.0
------

*Released: 2015-07-16*

- Initial release. [drybjed]
