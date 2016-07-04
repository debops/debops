Changelog
=========

**debops.php**

Copyright (C) 2015-2016 `DebOps Project <http://debops.org/>`_

License: `GNU General Public License v3 <https://www.tldrlegal.com/l/gpl-3.0>`_

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.


Contributors
------------

- [drybjed] - `Maciej Delmanowski <https://github.com/drybjed/>`_  (role maintainer)
- [mbarcia] - `Mariano Barcia <https://github.com/mbarcia/>`_


Unreleased
----------

Added
~~~~~

- Added support for PHP7 installed from OS releases that have it available.
  [mbarcia]

- Role now exposes an additional ``php__dependent_packages`` list which can be
  used by other Ansible roles to install PHP packages for the current version
  without the need for the other roles to know what PHP version is installed.
  [drybjed]

Changed
~~~~~~~

- Renamed all role variables from ``php5_*`` to ``php__*`` to make role
  unversal between major PHP versions and put its variables in a separate
  namespace. [mbarcia]

- Converted Changelog to a new format. [drybjed]

- Redesigned APT package support.

  Role now detects what PHP package versions are available and installs the
  highest one available. An optional Ondřej Surý APT/PPA repository can be
  enabled on Debian or Ubuntu distributions to provide newer version of
  packages if desired. [drybjed]

Removed
~~~~~~~

- The ``php__version`` variable cannot be set directly; istead the available
  PHP version is detected at role execution and stored in Ansible local facts
  to ensure idempotency. The autodetected PHP version can be influenced by
  order of the package names in ``php__version_preference`` list. [drybjed]

v0.1.0 - 2016-06-01
-------------------

Added
~~~~~

- Add Changelog. [drybjed]

