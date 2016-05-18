Changelog
=========

v0.2.0
------

*Released: 2016-05-18*

- Role has been redesigned from scratch. It now supports local as well as
  remote logs, forwarding over UDP, TCP and TLS. Configuration is defined in
  default variables which can be easily overriden if necessary. New
  documentation has been written as well. [drybjed]

v0.1.0
------

*Released: 2016-05-18*

- Add Changelog. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [ypid]

- Default to ``enabled: True`` in ``rsyslog_pools``.
  Before this, an entry missing a ``enabled`` has been ignored. [ypid]

