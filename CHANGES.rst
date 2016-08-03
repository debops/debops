Changelog
=========

**debops-contrib.roundcube**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is ganto.


`debops-contrib.roundcube master`_ - unreleased
-----------------------------------------------

.. _debops-contrib.roundcube master: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.0...master

Changed
~~~~~~~

- Introduced playbook-based role dependencies and removed hard-dependencies on
  optional roles. For this reason the role variable ``roundcube__dependencies``
  was removed too. If no or only individual dependencies are required simply
  adjust the playbook accordingly. [ganto]

- Converted documentation/Changelog to a new format. [ganto]


debops-contrib.roundcube v0.1.0 - 2016-06-14
--------------------------------------------

Added
~~~~~

- Initial release of Roundcube 1.1.5 with SQLite and MySQL support. [ganto]
