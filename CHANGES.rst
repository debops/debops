Changelog
=========

**debops.java**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.java master`_ - unreleased
----------------------------------

.. _debops.java master: https://github.com/debops/ansible-java/compare/v0.1.1...master


`debops.java v0.1.1`_ - 2017-01-25
----------------------------------

.. _debops.java v0.1.1: https://github.com/debops/ansible-java/compare/v0.1.0...v0.1.1

Added
~~~~~

- Install ``ca-certificates-java`` package to keep system CA certificate store
  and Java CA certificate store synchronized. [drybjed_]


debops.java v0.1.0 - 2016-07-18
-------------------------------

Added
~~~~~

- Add documentation and Changelog. [drybjed]

Changed
~~~~~~~

- Switch from installing specific version of OpenJDK to a Debian OpenJDK
  metapackage which installs the default headless version of OpenJRE for
  current OS release. [drybjed]
