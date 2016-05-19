Changelog
=========

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

