Changelog
=========

.. include:: includes/all.rst

**debops.etc_services**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed_.


`debops.etc_services master`_ - unreleased
------------------------------------------

.. _debops.etc_services master: https://github.com/debops/ansible-etc_services/compare/v0.3.0...master

Changed
~~~~~~~

- Updated documentation and changelog according to latest guidelines. [ganto_]



`debops.etc_services v0.3.0`_ - 2016-04-25
------------------------------------------

.. _debops.etc_services v0.3.0: https://github.com/debops/ansible-etc_services/compare/v0.2.0...v0.3.0

Added
~~~~~

- Added ``delete`` boolean switch to allow to delete local services. [ypid_]

- Add support for ``item.state`` parameter. [drybjed_]

Changed
~~~~~~~

- Condense the :command:`dpkg-divert` revert tasks into one. [drybjed_]


`debops.etc_services v0.2.0`_ - 2016-03-14
------------------------------------------

.. _debops.etc_services v0.2.0: https://github.com/debops/ansible-etc_services/compare/v0.1.0...v0.2.0

Added
~~~~~

- Wrote documentation. [ypid_]

Changed
~~~~~~~

- Reworked role, updated metadata. [ypid_]

- Renamed ``etc_services`` to :envvar:`etc_services__enabled`. [ypid_]

- Renamed ``etc_services_([^_].+)`` to ``etc_services__\1``.
  Old list variables are deprecated but still work for now. [ypid_]

- Change the task conditions to test for boolean values instead of only
  checking if a variable is defined. [drybjed_]


debops.etc_services v0.1.0 - 2016-03-14
---------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
