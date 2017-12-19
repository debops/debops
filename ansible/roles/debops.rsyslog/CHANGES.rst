.. _rsyslog__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.rsyslog**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.rsyslog master`_ - unreleased
-------------------------------------

.. _debops.rsyslog master: https://github.com/debops/ansible-rsyslog/compare/v0.2.1...master


`debops.rsyslog v0.2.1`_ - 2017-02-03
-------------------------------------

.. _debops.rsyslog v0.2.1: https://github.com/debops/ansible-rsyslog/compare/v0.2.1...v0.2.0

Added
~~~~~

- Add support for anonymous TLS connections, as well as a way to allow only TLS
  connections. [bleuchtang]

Changed
~~~~~~~

- Update role documentation and Changelog. [drybjed_]

Fixed
~~~~~

- Make sure that the original files that are diverted when the role is enabled
  are not removed when the role is executed multiple times. [drybjed_]


`debops.rsyslog v0.2.0`_ - 2016-05-18
-------------------------------------

.. _debops.rsyslog v0.2.0: https://github.com/debops/ansible-rsyslog/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Role has been redesigned from scratch. It now supports local as well as
  remote logs, forwarding over UDP, TCP and TLS. Configuration is defined in
  default variables which can be easily overridden if necessary. New
  documentation has been written as well. [drybjed_]


debops.rsyslog v0.1.0 - 2016-05-18
----------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

Changed
~~~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [ypid_]

- Default to ``enabled: True`` in ``rsyslog_pools``.
  Before this, an entry missing a ``enabled`` has been ignored. [ypid_]
