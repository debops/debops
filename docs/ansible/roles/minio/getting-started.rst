Getting started
===============

.. contents::
   :local:


Default installation and upgrades
---------------------------------

The role will install the latest MinIO release available by default. After
that, the selected release will be "locked" via the Ansible local facts, and
normal execution of the :ref:`debops.minio` role will not upgrade an existing
installation.

To perform an upgrade, you can use the following command:

.. code-block:: yaml

   debops service/minio -l <host|group> -t role::golang \
                        -e 'minio__upstream_upgrade=true'

This command will execute the :ref:`debops.golang` Ansible role in the context
of the :file:`service/minio` playbook and perform the upgrade of MinIO binary
if a new release is found. The existing MinIO instances will be restarted
afterwards.

If you want to perform upgrades automatically when the role is executed when
they are available, you can set the :envvar:`minio__upstream_upgrade` variable
to ``True`` in the Ansible inventory.

The previously downloaded MinIO releases are currently not removed
automatically, therefore make sure that you clean up the
:file:`~_golang/go/src/` directory managed by the :ref:`debops.golang` role
from time to time.


Dependent role usage
--------------------

The :ref:`debops.minio` role is focused on configuration of the MinIO service,
and relies on other DebOps roles for the actual installation and configuration
of additional services:

- The :ref:`debops.golang` role is used to download and verify MinIO binary, or
  clone the MinIO source code and build the binary locally.

- The :ref:`debops.keyring` role is used by the :ref:`debops.golang` role to
  fetch and import the MinIO GPG signing key used to verify the MinIO binaries
  or source code.

- The :ref:`debops.pki` role (not included in the playbook) is used to provide
  the PKI infrastructure and X.509 certificates required for TLS connections to
  MinIO instances.

- The :ref:`debops.sysctl` and :ref:`debops.sysfs` roles are used to configure
  kernel parameters in the :file:`/proc/` and :file:`/sys/` directories related
  to MinIO.

- The :ref:`debops.nginx` role is used to configure the web server access to
  MinIO service over HTTPS and redirects the subdomain queries to the correct
  MinIO instances configured on the host.

- The :ref:`debops.ferm` role is used to open the firewall access to MinIO
  instances via their TCP ports.

See the provided Ansible playbook for the order of the roles and usage of the
dependent role variables. Without the mentioned DebOps roles and services
managed by them, :ref:`debops.minio` role alone will not deploy the MinIO
service correctly.


Example inventory
-----------------

To configure MinIO service on a host, it needs to be added to the
``[debops_service_minio]`` Ansible inventory group:

.. code-block:: none

   [debops_service_minio]
   hostname

See the :ref:`minio__ref_deployment_guide` more examples of distributed MinIO
deployments.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.minio`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/minio.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::minio``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.minio`` Ansible role:

- `MinIO documentation`__

  .. __: https://docs.min.io/
