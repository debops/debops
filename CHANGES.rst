Changelog
=========

**debops.nodejs**

Copyright (C) 2015-2016 DebOps Project (http://debops.org/)

License: `GNU General Public License v3 <https://www.tldrlegal.com/l/gpl-3.0>`_

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.


Contributors
------------

- [drybjed] - `Maciej Delmanowski <https://github.com/drybjed/>`_  (role maintainer)
- [patrickheeney] - `Patrick Heeney <https://github.com/patrickheeney/>`_


Unreleased
----------


v0.3.0 - 2016-07-01
-------------------

Added
~~~~~

- The ``nodejs__upstream`` boolean variable selects which NodeJS release should
  be installed. If set to ``False`` (default), the role will install packages
  from current OS release. If it's set to ``True``, role will install packages
  from `NodeSource <https://nodesource.com/>`_ repository. [drybjed]

Changed
~~~~~~~

- Switched the Changelog to a new format. List of role maintainers is moved to
  Changelog for easier maintenance. [drybjed]

- All role variables are renamed from ``nodejs_*`` to ``nodejs__*`` to put them
  in their own namespace. [drybjed]

- The ``nodejs_upstream`` variable is renamed to ``nodejs__upstream_version``.
  The default upstream version is NodeJS 4.x. [drybjed]

- Role will now install OS release NodeJS packages by default, to adhere to
  DebOps Software Policy. [drybjed]

- The ``nodejs_npm_global_packages`` has been renamed to
  ``nodejs__npm_packages``. [drybjed]

- The ``nodejs__npm_*`` package lists support all of the ``npm`` Ansible module
  parameters. [drybjed]

- The role uses ``package`` Ansible module instead of ``apt`` to install
  packages. [drybjed]

Removed
~~~~~~~

- The ``nodejs-legacy`` package is not installed by default. [drybjed]


v0.2.0 - 2016-06-29
-------------------

Changed
~~~~~~~

- Rename ``nodejs_upstream_repo`` to ``nodejs_upstream_repository``
  for consistency with other ``debops`` roles. [patrickheeney]

- Rename ``nodejs_npm_packages`` to ``nodejs_npm_global_packages``
  to better reflect their purpose. [patrickheeney]

- Rename ``nodejs_packages`` to ``nodejs_base_packages`` to allow
  ``nodejs_packages`` to be used for user packages. [patrickheeney]

- Refactor apt keys and apt repositories. [patrickheeney]

Removed
~~~~~~~

- Remove npm installer as it is now bundled with node.js.
  [patrickheeney]

- Remove npm /tmp directory override. It will now use npm defaults.
  [patrickheeney]


v0.1.0 - 2015-09-20
-------------------

Added
~~~~~

- Initial release. [drybjed]

