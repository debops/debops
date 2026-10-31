.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _gh_ci_pipeline:

GitHub Actions CI pipeline
==========================

The `DebOps CI Pipeline <https://github.com/debops/debops/blob/master/.github/workflows/debops-ci-pipeline.yml>`__
GitHub Actions workflow applies the DebOps playbooks defined in the role
manifest (:file:`lib/tests/gh-ci-pipeline/roles.yml`) on a GitHub-hosted
Ubuntu runner, using the :command:`debops` command. Each manifest entry is
tested in isolation: the playbook is applied twice, and the second
application must not report any changes - an idempotency check inherited
from the older GitLab CI-based "Jane" test framework.

The :command:`matrix.py` script in the same directory renders the manifest
into the workflow's job matrix. It is run by the workflow itself and can be
executed locally to preview or validate the manifest:

.. code-block:: console

   python3 lib/tests/gh-ci-pipeline/matrix.py --all

Role manifest
-------------

Each entry in :file:`roles.yml` describes a single test job. The fields
are:

``name``
  Unique identifier of the test entry, shown as the job name in the
  workflow. Entries that test the same playbook in different scenarios
  distinguish themselves here.

``role``
  Name of the role whose changes select the entry in path filtering.
  Defaults to the entry name. Set it explicitly when an entry tests
  a playbook under a scenario-specific name:

  .. code-block:: yaml

     - name: 'postgresql_server-replica'
       playbook: 'service/postgresql_server'
       role: 'postgresql_server'

``playbook``
  Playbook executed by :command:`debops run`, relative to the
  :file:`ansible/playbooks/` directory of a DebOps project. Defaults to
  the entry name. A list of playbooks can be specified instead, to apply
  them in order on the same host: the playbooks are applied one by one,
  and then the idempotency check re-applies each of them in the same
  order, so that later playbooks see the state applied by the earlier
  ones.

``always``
  When set, the entry runs on every CI invocation, regardless of the
  changed paths. The ``bootstrap`` and ``common`` playbooks are always
  tested this way, providing a base smoke test for each change.

``groups``
  List of Ansible inventory groups that the test host is added to before
  the playbook is applied. Most of the :file:`service/` playbooks only
  run against hosts in the ``debops_service_<name>`` group.

``inventoryspec``
  Inventory specification applied to the test project before the playbook
  runs, using the :command:`debops project refresh --template - --force`
  command. The value is an inventory specification YAML dictionary, see
  :ref:`inventory_specification` for its format. Use it to configure test
  scenarios: define the inventory hosts and groups, set group variables
  that select a specific service backend and so on. The specification is
  applied after the entry's ``groups`` and can replace the files generated
  during project initialization, including the :file:`hosts` file. The
  ``pipe()`` and ``include()`` functions of specification version 3 are
  not enabled in the pipeline.

``packages``
  List of APT packages installed on the runner in addition to the base
  set prepared by the workflow.

``pre_script``
  Shell commands executed in the project directory after its
  initialization, before the playbook is applied.

``post_script``
  Shell commands executed in the project directory with the virtualenv
  active after the playbook applications, used to test the service
  behavior. A non-zero exit status of the script fails the job.

``vars``
  Reserved for per-entry Ansible variable overrides. Not consumed yet;
  entries that define it are rejected by the :command:`matrix.py` script
  until support is implemented.

``runner``
  GitHub Actions runner image used by the job. Defaults to
  ``ubuntu-24.04``.

``timeout``
  Job timeout in minutes. Defaults to 30 minutes, so that a hung service
  cannot occupy a runner until the global 6 hour timeout.

``idempotency``
  ``strict`` (default) fails the job when the second playbook application
  still reports changes; ``advisory`` only issues a warning. Entries
  added to the manifest start as ``advisory`` and are flipped to
  ``strict`` once verified clean.

``excluded``, ``reason``
  Entries that cannot be tested on the hosted runners are kept in the
  manifest with ``excluded: True`` and a ``reason`` field that documents
  why. The :command:`matrix.py` script skips them.

Path filtering
--------------

On pull requests, the workflow diffs the pull request against its base
branch and selects the entries to run:

- Entries marked as ``always`` are run unconditionally.
- Changes under a role tree select the entries whose ``role`` field
  matches that role.
- Changes that affect the whole pipeline - shared Ansible configuration,
  the APT requirements used to prepare the environment, or a role without
  its own test entry - select the full matrix, since such a role can be
  a dependency of any playbook.
- Pushes to any branch run the full matrix.

The base runner image
---------------------

The tests run on GitHub-hosted runners running the ``ubuntu-24.04`` image.
Unlike a freshly installed Ubuntu server, the image is a curated developer
toolset, rebuilt weekly; its exact contents at each build are listed in the
auto-generated `Ubuntu2404-Readme.md`__ file in the ``actions/runner-images``
repository, and the image version used by a job is visible in its log.

.. __: https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md

Most of the preinstalled software is inert, but some of it interacts with the
DebOps roles under test:

- The ``mysql`` and ``postgresql`` servers are installed, with a MySQL instance
  configured with the ``root``/``root`` credentials and an initialized
  PostgreSQL cluster, both with the service disabled. The
  :ref:`debops.mariadb_server` and :ref:`debops.postgresql_server` roles
  encounter existing cluster state instead of an empty host.
- The ``apache2`` and ``nginx`` servers are installed and preconfigured to
  listen on port 80, with the services inactive.
- The Docker daemon is running, together with containerd, Docker Compose and
  Podman; the :ref:`debops.docker_server` role replaces the daemon under it.
- PHP with the Xdebug extension, Ruby, Node.js with the ``n`` and ``nvm``
  version managers, and several OpenJDK releases are preinstalled, which
  changes what the :ref:`debops.php`, :ref:`debops.ruby`, :ref:`debops.nodejs`
  and :ref:`debops.java` roles find on the host.
- The systemd-resolved stub resolver owns the local DNS on ``127.0.0.53`` and
  the systemd-timesyncd service is active, which the :ref:`debops.unbound`,
  :ref:`debops.bind`, :ref:`debops.dnsmasq`, :ref:`debops.resolvconf` and
  :ref:`debops.ntp` roles need to account for.
- The ``openssh-server`` package is installed and its host keys exist, so the
  :ref:`debops.sshd` role does not exercise the fresh-install path.
- The platform itself provides facts that differ from a self-hosted host:
  the primary interface is managed by netplan and systemd-networkd, IPv6 is
  not available, a swap file is active and the hostname is a random
  runner-generated name.

The image does not ship snapd, unattended-upgrades, ufw or LXD, so the
corresponding interference present on a default Ubuntu installation does not
apply here.

The image contents change from week to week; the ``runner`` field of the
manifest entry pins the operating system release, while the image build rolls.
Role entries should not rely on the specific preinstalled versions, only on
their presence or absence.

Neutralizing image defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Entries that are affected by the preinstalled state use the ``pre_script``
and ``post_script`` hooks to compensate. Prefer asserting the state that
DebOps manages over removing the preinstalled one: a service test that
passes against the preinstalled server but fails against the DebOps-managed
one is exactly the regression the pipeline should catch.

Stop a preinstalled service before the playbook runs, so that the role
manages the service start and finds no competing daemon:

.. code-block:: yaml

   - name: 'docker_server'
     playbook: 'service/docker_server'
     pre_script: |
       sudo systemctl stop docker.service docker.socket containerd.service

Test the service through the socket or interface DebOps configures, so that
the test fails if the preinstalled server is answering instead of the
role-managed one:

.. code-block:: yaml

   - name: 'mariadb_server'
     playbook: 'service/mariadb_server'
     groups: [ 'debops_service_mariadb_server' ]
     post_script: |
       mariadb --socket /run/mysqld/mysqld.sock -e 'SELECT VERSION();'

Disable the daily APT maintenance timers when a job is sensitive to
background package operations holding the dpkg lock:

.. code-block:: yaml

   pre_script: |
     sudo systemctl stop apt-daily.timer apt-daily-upgrade.timer
     sudo systemctl mask apt-daily.service apt-daily-upgrade.service

Removing the preinstalled packages with :command:`apt-get purge` makes the
install path of a role fully clean, at the cost of additional job time; use
it only when the difference between installing and reconfiguring the service
matters for the test.

Excluded roles
--------------

Roles that cannot be meaningfully tested on the GitHub-hosted runners
(kernel module and hardware management like ``debops.kmod`` and
``debops.hwraid``, bootloader and network interface reconfiguration,
roles that require a LAN segment or more resources than a hosted runner
provides) are kept in the manifest with the ``excluded`` field set and
a ``reason`` describing why they are skipped, so that the state of the
pipeline is visible in one place.
