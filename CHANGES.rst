Changelog
=========

.. include:: includes/all.rst

**debops.java**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.java master`_ - unreleased
----------------------------------

.. _debops.java master: https://github.com/debops/ansible-java/compare/v0.2.0...master

Added
~~~~~

- Add Ansible local facts for the ``debops.java`` role. [drybjed_]

- Add a way to conditionally install the Java Development Kit environment if
  needed. [drybjed_]


`debops.java v0.2.0`_ - 2017-05-01
----------------------------------

.. _debops.java v0.2.0: https://github.com/debops/ansible-java/compare/v0.1.1...v0.2.0

Added
~~~~~

- Allow configuration of Java alternatives. [pedroluislopez_]

- Install OpenJDK 8 on Debian Jessie by default using packages provided via
  Backports, if the Backports repository is configured. [drybjed_]

Fixed
~~~~~

- Fix warning about wrong use of the ``{{ }}`` in ``when:`` conditions on newer
  Ansible versions. [drybjed_]


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

- Add documentation and Changelog. [drybjed_]

Changed
~~~~~~~

- Switch from installing specific version of OpenJDK to a Debian OpenJDK
  metapackage which installs the default headless version of OpenJRE for
  current OS release. [drybjed_]
