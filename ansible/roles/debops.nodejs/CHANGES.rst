.. _nodejs__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.nodejs**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.nodejs master`_ - unreleased
------------------------------------

.. _debops.nodejs master: https://github.com/debops/ansible-nodejs/compare/v0.3.1...master


`debops.nodejs v0.3.1`_ - 2017-03-08
------------------------------------

.. _debops.nodejs v0.3.1: https://github.com/debops/ansible-nodejs/compare/v0.3.0...v0.3.1

Changed
~~~~~~~

- Change the default NodeJS version installed from upstream repositories from
  ``4.x`` to ``6.x`` to keep support for older OS releases. [bfabio_]

- Update documentation and Changelog. [drybjed_]

- The role now tracks the status of :envvar:`nodejs__upstream` variable and can
  automatically upgrade the NodeJS packages from the OS-distributed version to
  an upstream version. You can use this to request NodeSource packages from
  a different Ansible role if needed.

  To do this effectively, role will automatically remove APT packages that were
  installed automatically and are no longer needed. This might impact other
  packages than just the ones related to NodeJS, but it's a one time operation;
  when upstream NodeJS packages are installed, they are not upgraded
  automatically by the role. [drybjed_]


`debops.nodejs v0.3.0`_ - 2016-07-01
------------------------------------

.. _debops.nodejs v0.3.0: https://github.com/debops/ansible-nodejs/compare/v0.2.0...v0.3.0

Added
~~~~~

- The :envvar:`nodejs__upstream` boolean variable selects which NodeJS release should
  be installed. If set to ``False`` (default), the role will install packages
  from current OS release. If it's set to ``True``, role will install packages
  from `NodeSource <https://nodesource.com/>`_ repository. [drybjed_]

Changed
~~~~~~~

- Switched the Changelog to a new format. List of role maintainers is moved to
  Changelog for easier maintenance. [drybjed_]

- All role variables are renamed from ``nodejs_*`` to ``nodejs__*`` to put them
  in their own namespace. [drybjed_]

- The ``nodejs_upstream`` variable is renamed to :envvar:`nodejs__upstream_version`.
  The default upstream version is NodeJS 4.x. [drybjed_]

- Role will now install OS release NodeJS packages by default, to adhere to
  DebOps Software Policy. [drybjed_]

- The ``nodejs_npm_global_packages`` has been renamed to
  :envvar:`nodejs__npm_packages`. [drybjed_]

- The ``nodejs__npm_*`` package lists support all of the ``npm`` Ansible module
  parameters. [drybjed_]

- The role uses ``package`` Ansible module instead of :command:`apt` to install
  packages. [drybjed_]

Removed
~~~~~~~

- The ``nodejs-legacy`` package is not installed by default. [drybjed_]


`debops.nodejs v0.2.0`_ - 2016-06-29
------------------------------------

.. _debops.nodejs v0.2.0: https://github.com/debops/ansible-nodejs/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Rename ``nodejs_upstream_repo`` to ``nodejs_upstream_repository``
  for consistency with other ``debops`` roles. [patrickheeney_]

- Rename ``nodejs_npm_packages`` to ``nodejs_npm_global_packages``
  to better reflect their purpose. [patrickheeney_]

- Rename ``nodejs_packages`` to ``nodejs_base_packages`` to allow
  ``nodejs_packages`` to be used for user packages. [patrickheeney_]

- Refactor apt keys and apt repositories. [patrickheeney_]

Removed
~~~~~~~

- Remove npm installer as it is now bundled with node.js.
  [patrickheeney_]

- Remove npm /tmp directory override. It will now use npm defaults.
  [patrickheeney_]


debops.nodejs v0.1.0 - 2015-09-20
---------------------------------

Added
~~~~~

- Initial release. [drybjed_]
