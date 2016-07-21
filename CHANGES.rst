.. _docker_gen__ref_changelog:

Changelog
=========

**debops.docker_gen**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.docker_gen master`_ - unreleased
----------------------------------------

.. _debops.docker_gen master: https://github.com/debops/ansible-docker_gen/compare/v0.2.0...master


`debops.docker_gen v0.2.0`_ - 2016-07-21
----------------------------------------

.. _debops.docker_gen v0.2.0: https://github.com/debops/ansible-docker_gen/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add missing ``upstart`` entry in service manager notification map. [vbehar]

Changed
~~~~~~~

- Update documentation and Changelog. [ypid, tallandtree, drybjed]

- Rename all role variables from ``docker_gen_*`` to ``docker_gen__*`` to move
  them into their own namespace. [tallandtree]

- ``*.changed`` is changed to ``*|changed`` to ensure correct variable type
  resolution by Ansible [tallandtree]

debops.docker_gen v0.1.0 - 2015-09-11
-------------------------------------

Added
~~~~~

- Initial release. [drybjed]
