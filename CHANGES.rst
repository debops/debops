Changelog
=========

.. include:: includes/all.rst

**debops.gitlab_runner**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.gitlab_runner master`_ - unreleased
-------------------------------------------

.. _debops.gitlab_runner master: https://github.com/debops/ansible-gitlab_runner/compare/v0.2.0...master


`debops.gitlab_runner v0.2.0`_ - 2017-08-16
-------------------------------------------

.. _debops.gitlab_runner v0.2.0: https://github.com/debops/ansible-gitlab_runner/compare/v0.1.2...v0.2.0

Added
~~~~~

- Add a separate list of tags defined for shell executors that describe the
  host in a greater detail. [drybjed_]

Changed
~~~~~~~

- Fixed Ansible warnings during task execution. [drybjed_]

- Update APT cache before first package installation. [azman0101, drybjed_]

- Convert the Ansible local facts to a Python script. The GitLab Runner state
  is stored in a separate, secure JSON file. [drybjed_]

- Redesign the list of default GitLab Runner executors. The role will create
  a 'shell' executor, unless Docker is detected in which case the 'shell'
  executor will be disabled. Two Docker executors will be created, one
  privileged and one unprivileged, with respective tags. [drybjed_]

- If Docker is detected, the ``gitlab-runner`` user will be added to the
  ``docker`` group to allow access to Docker containers. [drybjed_]

- On hosts with Docker executors, number of concurrent jobs will depend on
  number of vCPUs available. Hosts with 'shell' executor will be allowed to run
  only 1 job at a time. [drybjed_]

- The default 'shell' and privileged Docker executors will not be allowed to
  run untagged jobs for security reasons. The default unprivileged Docker
  executor can still run untagged jobs. [drybjed_]

Fixed
~~~~~

- Fixed an error with missing Ansible facts breaking GitLab Runner registration. [drybjed_]


`debops.gitlab_runner v0.1.2`_ - 2016-10-05
-------------------------------------------

.. _debops.gitlab_runner v0.1.2: https://github.com/debops/ansible-gitlab_runner/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Added distributed cache bucket location configuration key. [sidewinder12s]


`debops.gitlab_runner v0.1.1`_ - 2016-08-12
-------------------------------------------

.. _debops.gitlab_runner v0.1.1: https://github.com/debops/ansible-gitlab_runner/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Add 201 as successful HTTP status on register. [bfabio]

- Update documentation and Changelog. [drybjed_]


debops.gitlab_runner v0.1.0 - 2016-04-11
----------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
