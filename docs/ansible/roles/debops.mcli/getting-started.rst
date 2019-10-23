Getting started
===============

.. contents::
   :local:


Default installation and upgrades
---------------------------------

The role will install the latest MinIO Client release available by default.
After that, the selected release will be "locked" via the Ansible local facts,
and normal execution of the :ref:`debops.mcli` role will not upgrade an
existing installation.

To perform an upgrade, you can use the following command:

.. code-block:: yaml

   debops service/mcli -l <host|group> -t role::golang \
                       -e 'mcli__upstream_upgrade=true'

This command will execute the :ref:`debops.golang` Ansible role in the context
of the :file:`service/mcli` playbook and perform the upgrade of MinIO Client
binary if a new release is found.

If you want to perform upgrades automatically when the role is executed when
they are available, you can set the :envvar:`mcli__upstream_upgrade` variable
to ``True`` in the Ansible inventory.

The previously downloaded MinIO Client releases are currently not removed
automatically, therefore make sure that you clean up the
:file:`~_golang/go/src/` directory managed by the :ref:`debops.golang` role
from time to time.


Dependent role usage
--------------------

The :ref:`debops.mcli` role is focused on configuration of the MinIO Client
install parameters, and relies on other DebOps roles for the actual
installation:

- The :ref:`debops.golang` role is used to download and verify MinIO Client
  binary, or clone the MinIO Client source code and build the binary locally.

- The :ref:`debops.keyring` role is used by the :ref:`debops.golang` role to
  fetch and import the MinIO Client GPG signing key used to verify the MinIO
  Client binaries or source code.

See the provided Ansible playbook for the order of the roles and usage of the
dependent role variables. Without the mentioned DebOps roles and services
managed by them, :ref:`debops.mcli` role alone will not deploy the MinIO Client
correctly.


Example inventory
-----------------

To configure MinIO Client on a host, it needs to be added to the
``[debops_service_mcli]`` Ansible inventory group:

.. code-block:: none

   [debops_service_mcli]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.mcli`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/mcli.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::mcli``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.mcli`` Ansible role:

- `MinIO documentation`__

  .. __: https://docs.min.io/
