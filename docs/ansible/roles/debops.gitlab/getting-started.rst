Getting started
===============

.. contents:: Sections
   :local:

Role design
-----------

The ``debops.gitlab`` role is designed to install the GitLab services using
`the source installation method <https://gitlab.com/gitlab-org/gitlab-ce/blob/master/doc/install/installation.md>`_.
This method, instead of GitLab Omnibus packages, was chosen to allow use of
other services managed by DebOps, like Redis, nginx, a SQL database, and so
on. To support monthly GitLab releases, the role tracks currently installed
version of GitLab and can perform an automatic upgrade when an older version is
detected. Latest changes to the active GitLab branch are also automatically
applied on Ansible runs, to support updates.

The installation or upgrade process is not ideal - role performs installation
or an upgrade when new changes are detected in the :command:`git` repositories,
but if there are errors during this process, role cannot recover from that
state automatically. It is advisable to keep a separate staging environment to
check for any issues with an upgrade of the currently installed production
environment before performing the production upgrade.

If a failed install or upgrade occurs, the easiest recovery method is usually
to completely reset the affected host (perform a new deployment) after fixing
the issue. The more involved method would be to remove the source
:command:`git` repositories and checked out directories and re-run the role
again.

SQL database support
--------------------

The ``debops.gitlab`` role automatically detects the available PostgreSQL database
using the Ansible local facts. If the database service should be present on the
same host as the GitLab service, adding the corresponding database server group in
the Ansible inventory should be enough.
If the database server is on a different host, you should use the corresponding
database client role to configure the relevant Ansible local facts before
running the ``debops.gitlab`` role.

Installation of a new GitLab environment with existing database is currently
not tested and may result in a broken installation or data corruption.

You can install the PostgreSQL database using its DebOps role.
See the :ref:`debops.postgresql_server` role documentation for more details.

Redis support
-------------

Currently the ``debops.gitlab`` role expects a Redis Server instance installed
on the host, for example by the :ref:`debops.redis_server` Ansible role.
Support for distributed Redis Server service managed by Redis Sentinel is
planned for a future release.

Support for other services
--------------------------

The ``debops.gitlab`` role depends on other DebOps roles to configure various
services used by GitLab and provide the required environment for installation.
The default role playbook is designed to install the services on the same host
as the GitLab service, however it should be possible to move them to other,
remote hosts if necessary.

The role provides its own set of :command:`systemd` unit files that allow
management of different GitLab services as one "unit" using :command:`systemd`
slice. The new units will be enabled automatically on all new installations on
hosts that use the :command:`systemd` service manager; on other, older hosts
the role should fallback to the init script provided by the upstream.

Example inventory
-----------------

To enable GitLab service on a host, it needs to be included in the
``[debops_service_gitlab]`` Ansible inventory group. You should also enable
a suitable PostgreSQL database and Redis Server service.

Example Ansible inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_postgresql_server]
   hostname

   [debops_service_redis_server]
   hostname

   [debops_service_gitlab]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.gitlab`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/gitlab.yml
   :language: yaml
