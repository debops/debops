Changelog
=========

.. include:: includes/all.rst

**debops.resources**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.resources master`_ - unreleased
---------------------------------------

.. _debops.resources master: https://github.com/debops/ansible-resources/compare/v0.2.0...master


`debops.resources v0.2.0`_ - 2017-05-04
---------------------------------------

.. _debops.resources v0.2.0: https://github.com/debops/ansible-resources/compare/v0.1.0...v0.2.0

Added
~~~~~

- Added pre- and post- task hooks to role to allow custom tasks to be added.
  [grantma_]

- Added custom delayed paths to allow to create symlinks to files created by this
  role. [ypid_]

- Support to create parent directories. [ypid_]

- Support the ``copy`` parameter in the ``unarchive`` module. [drybjed_]

- Add missing tags in the parent directory task. [drybjed_]

- Add support for cloning or updating :command:`git` repositories. [drybjed_]

Changed
~~~~~~~

- Update documentation, clean up default RST syntax and folds. [drybjed_]

- Update the list of supported parameters in the ``unarchive`` module.
  [drybjed_]

Fixed
~~~~~

- Don’t require ``item.src`` or ``item.content`` to delete files. [ypid_]

Removed
~~~~~~~

- The ``copy`` parameter of the ``unarchive`` module has been deprecated in
  favor of the ``remote_src`` parameter, therefore it was removed from the role
  to fix an issue with the ``copy()`` Python method having the same name.
  [drybjed_]


debops.resources v0.1.0 - 2016-06-21
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
