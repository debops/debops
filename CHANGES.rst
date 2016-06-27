Changelog
=========

v0.1.0
------

*Released: 2016-06-27*

- Add Changelog. [drybjed]

- Role has been redesigned and cleaned up.

  All role variables have been renamed to use a custom namespace.

  The role will no longer use ``debops.backporter`` role to build backported
  Ruby packages. This change will impact new Debian Wheezy installations if
  Ruby 2.1 was required there, however since Debian Jessie is now Stable, the
  need to backport packages every time is obsolete.

  You can install Ruby gems system-wide, or on a specific user account using
  custom list variables. User accounts will be created if necessary. [drybjed]

