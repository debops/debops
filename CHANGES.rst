Changelog
=========

v0.1.2
------

*Released: 2016-02-22*

- Use more granular lookup for security and release origins.

  Due to the ``unattended-upgrades`` `Debian Bug #704087 <https://bugs.debian.org/704087>`_
  on Debian Wheezy which stops the upgrades from being performed,
  ``debops.unattended_upgrades`` role will now use more granular lookup strings
  to select security and release origin patterns for current OS release.
  [drybjed]

v0.1.1
------

*Released: 2016-02-10*

- Rename all variables to create a virtual namespace. [drybjed]

v0.1.0
------

*Released: 2016-02-09*

- Initial release. [drybjed]

