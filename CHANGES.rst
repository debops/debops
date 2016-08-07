Changelog
=========

v0.2.1
------

*Released: 2016-08-07*

- Make sure that ``/etc/hosts.deny`` file exists. [drybjed]

v0.2.0
------

*Released: 2016-05-27*

- Role has been cleaned up and documented. The default variables have been
  renamed from ``tcpwrappers_`` to ``tcpwrappers__`` to indicate the separate
  namespace (some of the old variables are still supported). Some of the old
  configuration parameters like ``item.enabled`` or ``item.disabled`` have been
  removed and ``item.state`` is used to control the configuration state.
  [drybjed]

v0.1.0
------

*Released: 2016-02-08*

- Add Changelog. [drybjed]

- Rename the ``tcpwrappers`` variable to ``tcpwrappers_enabled`` and clean up
  of some tasks to use YAML format. [drybjed]

- Move a variable from ``vars/main.yml`` to ``defaults/main.yml``. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Small clean up of logic in templates, add support for ``debops.core``
  ``ansible_controllers`` variable. [drybjed]

