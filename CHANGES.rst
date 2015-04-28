Changelog
=========

v0.1.1
------

*Unreleased*

- Backport repositories have been redesigned to support distribution upgrades.

  Role will set up repositories for Debian Backports for current release,
  previous release and next release, with corresponding symlinks. When a new
  release comes around, this should let existing repositories easily migrate
  from "stable" to "oldstable" and create new "stable" repository for new
  release. [drybjed]

- By default, Debian Backport repositories will support ARM architectures in
  addition to AMD64 and i386. [drybjed]

- ``reprepro_uploaders_local`` variable has been renamed to
  ``reprepro_uploaders_default_rules`` to allow split between "local"
  repositories and repositories for distribution backports. [drybjed]

- Export repositories when configuration of distributions managed on the server
  changes. [drybjed]

v0.1.0
------

*Released: 2015-04-26*

- First release. [drybjed]

