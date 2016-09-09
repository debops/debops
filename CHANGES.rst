.. _docker__ref_changelog:

Changelog
=========

**debops.docker**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer is drybjed.


`debops.docker master`_ - unreleased
------------------------------------

.. _debops.docker master: https://github.com/debops/ansible-docker/compare/v0.2.1...master

Added
~~~~~
- Ferm hook to restart docker daemon after ferm is restarted if :any:`docker__ferment`
  is set to False. [tallandtree]

Changed
~~~~~~~

- Docker daemon listens on port 2376 when TLS is used. [tallandtree]

`debops.docker v0.2.1`_ - 2016-08-29
------------------------------------

.. _debops.docker v0.2.1: https://github.com/debops/ansible-docker/compare/v0.2.0...v0.2.1

Added
~~~~~

- Support for dockerd (docker-engine 1.12). [tallandtree]

- Support for live restore (:any:`docker__live_restore`) of docker daemon
  (docker-engine 1.12) and other options. [tallandtree]

Changed
~~~~~~~

- Systemd configuration improved. [tallandtree]

- Support ``http_proxy``, ``https_proxy`` and ``no_proxy`` variables for Upstart
  systems. [tallandtree]

- Use custom distribution and release local facts for Docker upstream
  repository configuration. [drybjed]

- Use list of administrator accounts provided by the ``debops.core`` role.
  [drybjed]


`debops.docker v0.2.0`_ - 2016-07-20
------------------------------------

.. _debops.docker v0.2.0: https://github.com/debops/ansible-docker/compare/v0.1.2...v0.2.0

Added
~~~~~

- Enable configuration of custom UDP ports in the firewall for additional
  services like ``consul``. [ddpaul]

- Install ``python-setuptools`` APT package. [antoineco]

- Add support for Docker behind a HTTP proxy using ``systemd`` service files.
  [tallandtree]

Changed
~~~~~~~

- Fix deprecation warnings in Ansible 2.1.0 related to bare and undefined
  variables. [antoineco]

- Update documentation and Changelog. [ypid, tallandtree, drybjed]

- Rename all role variables from ``docker_*`` to ``docker__*`` to move them
  into their own namespace. [tallandtree]

- ``*.changed`` is changed to ``*|changed`` to ensure correct variable type
  resolution by Ansible. [tallandtree]


`debops.docker v0.1.2`_ - 2015-12-19
------------------------------------

.. _debops.docker v0.1.2: https://github.com/debops/ansible-docker/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add a default list variable which can be used to open additional ports in the
  firewall for Docker-related services. [drybjed]

- Create :file:`/etc/systemd/system` directory if not present for the Docker
  systemd unit file. [drybjed]


`debops.docker v0.1.1`_ - 2015-12-13
------------------------------------

.. _debops.docker v0.1.1: https://github.com/debops/ansible-docker/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Remove hard role dependencies and move additional role configuration to
  default variables. Ansible playbook can use this configuration to set up
  firewall rules and reserve ports in :file:`/etc/services`. [drybjed]

- Check if ``ansible_ssh_user`` contains a value before adding the default user
  to ``docker`` group, otherwise use name of the user account running the
  Ansible playbook. [drybjed]


debops.docker v0.1.0 - 2015-09-06
---------------------------------

Added
~~~~~

- Initial release. [drybjed]
