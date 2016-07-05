Changelog
=========

**debops.logrotate**

Copyright (C) 2016 `DebOps Project <http://debops.org/>`_

License: `GNU General Public License v3 <https://www.tldrlegal.com/l/gpl-3.0>`_

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.


Contributors
------------

- [drybjed] - `Maciej Delmanowski <https://github.com/drybjed/>`_  (role maintainer)


Unreleased
----------


v0.1.2 - 2016-07-05
-------------------

Fixed
~~~~~

- Role will now correctly divert/revert ``logrotate`` configuration files for
  packages that are not yet installed. This fixes an issue where specified file
  not present in the filesystem was diverted on each run, breaking idempotency.
  [drybjed]

v0.1.1 - 2016-05-18
-------------------

Changed
~~~~~~~

- Allow configuration of ``logrotate`` options common to all logs when no
  specific logs are set. [drybjed]


v0.1.0 - 2016-04-15
-------------------

Added
~~~~~

- Initial release. [drybjed]

