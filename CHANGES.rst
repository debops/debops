Changelog
=========

v0.1.2
------

*Released: 2015-10-27*

- Rewrite the ``/etc/lvm/lvm.conf`` configuration. Instead of using
  ``lineinfile`` Ansible module to modify the original, use a normal template
  to generate the configuration from scratch using a base LVM configuration and
  modifying it by user variables. [drybjed]

v0.1.1
------

*Released: 2015-07-16*

- Remove unnecessary comments from ``defaults/main.yml``. [drybjed]

v0.1.0
------

*Released: 2015-07-16*

- Initial release. [drybjed]

