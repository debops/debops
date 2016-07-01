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

Changed
~~~~~~~

- Renamed all role variables from ``php5_*`` to ``php__*`` to make role
  unversal between major PHP versions and put its variables in a separate
  namespace. [mbarcia]

- Converted Changelog to a new format. [drybjed]

v0.1.0 - 2016-06-01
-------------------

Added
~~~~~

- Add Changelog. [drybjed]

