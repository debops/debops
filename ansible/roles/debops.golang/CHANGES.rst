.. _golang__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.golang**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.golang master`_ - unreleased
------------------------------------

.. _debops.golang master: https://github.com/debops/ansible-golang/compare/v0.1.2...master

Changed
~~~~~~~

- Enable backported Go 1.8 packages in Debian Stretch. [bfabio]


`debops.golang v0.1.2`_ - 2017-09-16
------------------------------------

.. _debops.golang v0.1.2: https://github.com/debops/ansible-golang/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Switch tests on Travis CI to Ubuntu Trusty. [drybjed_]


`debops.golang v0.1.1`_ - 2016-10-21
------------------------------------

.. _debops.golang v0.1.1: https://github.com/debops/ansible-golang/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- Enable backported Go packages in Debian Jessie. The newer version of the Go
  environment is required by some newer applications, like GitLab. [bfabio, drybjed_]


debops.golang v0.1.0 - 2016-06-28
---------------------------------

Changed
~~~~~~~

- Role rewrite and first release.

  The hard dependency on debops.backporter_ role has been removed, now role
  uses debops.apt_preferences_ to install Go packages from backports on
  older OS releases. [drybjed_]
