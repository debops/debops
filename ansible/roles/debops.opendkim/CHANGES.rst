Changelog
=========

.. include:: includes/all.rst

**debops.opendkim**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.opendkim master`_ - unreleased
--------------------------------------

.. _debops.opendkim master: https://github.com/debops/ansible-opendkim/compare/v0.2.0...master


`debops.opendkim v0.2.0`_ - 2017-10-20
--------------------------------------

.. _debops.opendkim v0.2.0: https://github.com/debops/ansible-opendkim/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Change the ``extract-domainkey-zone`` script to be more friendly to BIND
  servers. [fpoulain, drybjed_]

Fixed
~~~~~

- Fix issues with OpenDKIM on Debian Stretch by enforcing the PIDFile and
  Socket paths in the OpenDKIM configuration file and :command:`systemd` unit.
  [fpoulain, drybjed_]


debops.opendkim v0.1.0 - 2017-09-04
-----------------------------------

Sponsors
~~~~~~~~

- The ``debops.opendkim`` Ansible role was sponsored by
  `Comp S.A. <https://www.comp.com.pl/en>`_.

Added
~~~~~

- Initial release. [drybjed_]
