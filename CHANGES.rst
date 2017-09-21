.. _docker__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.docker**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.docker master`_ - unreleased
------------------------------------

.. _debops.docker master: https://github.com/debops/ansible-docker/compare/v0.4.1...master


`debops.docker v0.4.1`_ - 2017-09-21
------------------------------------

.. _debops.docker v0.4.1: https://github.com/debops/ansible-docker/compare/v0.4.0...v0.4.1

Changed
~~~~~~~

- Install the ``virtualenv`` APT package conditionally depending on
  distribution release. [gasuketsu]


`debops.docker v0.4.0`_ - 2017-09-18
------------------------------------

.. _debops.docker v0.4.0: https://github.com/debops/ansible-docker/compare/v0.3.0...v0.4.0

Added
~~~~~

- Install :command:`docker-compose` from PyPI in a Python virtualenv
  environment, when upstream Docker support is enabled. The script will be
  available system-wide via a symlink in :file:`/usr/local/bin/` directory.
  [drybjed_]

Changed
~~~~~~~

- Change the :command:`ferm` post-hook script into an Ansible template.
  [drybjed_]

- Install :command:`ferment` from PyPI in a Python virtualenv environment to
  separate it from the system Python environment. Ferment is only installed
  when upstream Docker is not enabled. [drybjed_]

Fixed
~~~~~

- Be more careful about interactions of the firewall with Docker and the init
  system. This should fix an issue where the host did not boot properly under
  :command:`systemd` since :command:`ferm` tried to restart Docker too early
  during the boot process. [drybjed_]

- The :command:`ferment` wrapper script should correctly skip
  :command:`ferment` execution if Docker service is not running. [drybjed_]


`debops.docker v0.3.0`_ - 2017-08-16
------------------------------------

.. _debops.docker v0.3.0: https://github.com/debops/ansible-docker/compare/v0.2.1...v0.3.0

Added
~~~~~

- Ferm hook to restart docker daemon after ferm is restarted if :envvar:`docker__ferment`
  is set to False. [tallandtree_]

- Use docker upstream repository by default on stretch installations [cultcom]

- Switch to docker-ce and docker-ee. [tallandtree_]

- Add the Ansible local facts for the ``debops.docker`` role so that other
  roles can detect if Docker is installed. [drybjed_]

Changed
~~~~~~~

- Docker daemon listens on port 2376 when TLS is used. [tallandtree_]


`debops.docker v0.2.1`_ - 2016-08-29
------------------------------------

.. _debops.docker v0.2.1: https://github.com/debops/ansible-docker/compare/v0.2.0...v0.2.1

Added
~~~~~

- Support for dockerd (docker-engine 1.12). [tallandtree_]

- Support for live restore (:envvar:`docker__live_restore`) of docker daemon
  (docker-engine 1.12) and other options. [tallandtree_]

Changed
~~~~~~~

- Systemd configuration improved. [tallandtree_]

- Support ``http_proxy``, ``https_proxy`` and ``no_proxy`` variables for Upstart
  systems. [tallandtree_]

- Use custom distribution and release local facts for Docker upstream
  repository configuration. [drybjed_]

- Use list of administrator accounts provided by the debops.core_ role.
  [drybjed_]


`debops.docker v0.2.0`_ - 2016-07-20
------------------------------------

.. _debops.docker v0.2.0: https://github.com/debops/ansible-docker/compare/v0.1.2...v0.2.0

Added
~~~~~

- Enable configuration of custom UDP ports in the firewall for additional
  services like ``consul``. [ddpaul]

- Install ``python-setuptools`` APT package. [antoineco]

- Add support for Docker behind a HTTP proxy using ``systemd`` service files.
  [tallandtree_]

Changed
~~~~~~~

- Fix deprecation warnings in Ansible 2.1.0 related to bare and undefined
  variables. [antoineco]

- Update documentation and Changelog. [ypid_, tallandtree_, drybjed_]

- Rename all role variables from ``docker_*`` to ``docker__*`` to move them
  into their own namespace. [tallandtree_]

- ``*.changed`` is changed to ``*|changed`` to ensure correct variable type
  resolution by Ansible. [tallandtree_]


`debops.docker v0.1.2`_ - 2015-12-19
------------------------------------

.. _debops.docker v0.1.2: https://github.com/debops/ansible-docker/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add a default list variable which can be used to open additional ports in the
  firewall for Docker-related services. [drybjed_]

- Create :file:`/etc/systemd/system` directory if not present for the Docker
  systemd unit file. [drybjed_]


`debops.docker v0.1.1`_ - 2015-12-13
------------------------------------

.. _debops.docker v0.1.1: https://github.com/debops/ansible-docker/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Remove hard role dependencies and move additional role configuration to
  default variables. Ansible playbook can use this configuration to set up
  firewall rules and reserve ports in :file:`/etc/services`. [drybjed_]

- Check if ``ansible_ssh_user`` contains a value before adding the default user
  to :command:`docker` group, otherwise use name of the user account running the
  Ansible playbook. [drybjed_]


debops.docker v0.1.0 - 2015-09-06
---------------------------------

Added
~~~~~

- Initial release. [drybjed_]
