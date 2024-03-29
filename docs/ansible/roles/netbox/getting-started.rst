.. Copyright (C) 2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


General deployment notes
------------------------

The application will by default be deployed both on ``ipam.{{ ansible_domain
}}`` as well as ``dcim.{{ ansible_domain }}`` DNS domains, for convenience.
You should either point these domains to the deployment host via DNS, or change
the :envvar:`netbox__fqdn` to set a desired subdomain.

By default NetBox will allow connections only to the specified DNS domains and
deny any other domain that might point to the host it's deployed on.

After the database initialization, the role will create an initial superuser
account with random password stored in the DebOps :file:`secret/` directory. The
username will be the first admin user defined by the :ref:`debops.core` Ansible
role.

By default anonymous access to NetBox is disabled.

NetBox configuration
--------------------

Since NetBox v3.1, some settings that traditionally could only be changed from
the :file:`configuration.py` file can now be changed without requiring a
restart of NetBox from within the web UI. Settings in the config file take
priority.

This is not supported by this role. Support for it would require changes to the
role. No valid use case has been presented to justify those changes.

The role is designed to manage multiple NetBox instances and allow to keep the
configuration in git. Both is not easily doable with dynamic configuration
settings.

For more details, refer to `dynamic configuration settings <https://netbox.readthedocs.io/en/stable/configuration/dynamic-settings/>`__.

The trend to move away from git by NetBox is observed
closely and additionally support for `Nautobot
<https://github.com/nautobot/nautobot>`__ might get added to DebOps at some
point because Nautobot takes git-like-version-control to the next level with
Dolt.

Python virtualenv support
-------------------------

The NetBox application will be deployed in a Python `virtualenv <http://virtualenv.org/>`_
environment to separate it from the system Python installation. By default the
environment will be created and maintained in the :file:`/usr/local/lib/netbox/`
directory using an unprivileged ``netbox`` account.

The NetBox Python requirements will be installed in the requested versions from
PyPI; this might take a while.

The role will install additional Python modules, ``gunicorn`` and
``setproctitle``, to support internal application server and/or management by
the system-wide ``gunicorn`` service.


Internal application server
---------------------------

The ``debops.netbox`` role can deploy NetBox with either a system-wide
``gunicorn`` service (default), or with an internal ``gunicorn`` application
sever using its own ``netbox`` ``systemd`` unit file. The role automatically
detects if the ``debops.gunicorn`` role has been deployed on a host and
switches between these modes as needed.


manage.py for NetBox power users
--------------------------------

The NetBox goody :file:`manage.py` is conveniently accessible using a script
that the role installs called :file:`netbox-manage`. It uses :command:`sudo` to
switch to the NetBox user, activates the virtualenv and run :file:`manage.py`.
Call it without parameters to see the available subcommands. The user calling
the script must have privileges to run commands as the NetBox system user.


Example inventory
-----------------

The NetBox application uses a PostgreSQL database as its backend, therefore you
need to setup a PostgreSQL server which the application can access. To
configure one on the same host as NetBox, add that host to the
``[debops_service_postgresql_server]`` Ansible inventory group. See the
:ref:`debops.postgresql_server` role documentation to see how to use the database
server remotely.

The Redis service is used for caching and is now required by NetBox as well.
The ``netbox__redis_*`` variables in the :ref:`debops.netbox` role can be used
to point NetBox to a remote Redis service; by default the role expects Redis to
be installed locally. You can deploy a Redis Server or cluster using the
:ref:`debops.redis_server` (and optionally :ref:`debops.redis_sentinel`)
Ansible roles. See their documentation for more details.

To deploy NetBox on a given host, you need to add that host to the
``[debops_service_netbox]`` Ansible inventory group. Complete, example
inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_redis_server]
   hostname

   [debops_service_postgresql_server]
   hostname

   [debops_service_netbox]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.netbox`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/netbox.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::netbox``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::netbox:config``
  Generate NetBox configuration file and restart the service if necessary.
