.. _ruby__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.ruby**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.ruby master`_ - unreleased
----------------------------------

.. _debops.ruby master: https://github.com/debops/ansible-ruby/compare/v0.1.1...master


`debops.ruby v0.1.1`_ - 2016-09-08
----------------------------------

.. _debops.ruby v0.1.1: https://github.com/debops/ansible-ruby/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add :envvar:`ruby__dev_support` boolean variable which can be used to install Ruby
  build environment even when no gems are requested. [drybjed_]

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]


debops.ruby v0.1.0 - 2016-06-27
-------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

Changed
~~~~~~~

- Role has been redesigned and cleaned up.

  All role variables have been renamed to use a custom namespace.

  The role will no longer use debops.backporter_ role to build backported
  Ruby packages. This change will impact new Debian Wheezy installations if
  Ruby 2.1 was required there, however since Debian Jessie is now Stable, the
  need to backport packages every time is obsolete.

  You can install Ruby gems system-wide, or on a specific user account using
  custom list variables. User accounts will be created if necessary. [drybjed_]
