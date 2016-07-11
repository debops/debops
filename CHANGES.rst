Changelog
=========

**debops.resources**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.resources master`_ - unreleased
---------------------------------------

.. _debops.resources master: https://github.com/debops/ansible-resources/compare/v0.1.0...master

Added
~~~~~

- Added custom delayed paths to allow to create symlinks to files created by this
  role. [ypid]

- Support to create parent directories. [ypid]

Fixed
~~~~~

- Don’t require ``item.src`` or ``item.content`` to delete files. [ypid]

debops.resources v0.1.0 - 2016-06-21
------------------------------------

Added
~~~~~

- Initial release. [drybjed]
