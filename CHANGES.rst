Changelog
=========

v0.1.0
------

*Released: 2016-06-28*

- Role rewrite and first release.

  The hard dependency on ``debops.backporter`` role has been removed, now role
  uses ``debops.apt_preferences`` to install Go packages from backports on
  older OS releases. [drybjed]

