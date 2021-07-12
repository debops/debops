.. Copyright (C) 2019 CipherMail B.V. https://www.ciphermail.com/
.. Copyright (C) 2019 Imre Jonk <imre@imrejonk.nl>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

Docker is available in two editions: Community Edition (CE) and Enterprise
Edition (EE). Docker EE is not supported on Debian distributions. See also:
`Docker variants`_.

.. _Docker variants: https://docs.docker.com/install/overview/

The Docker CLI package will be installed from the upstream repository by
default, because there currently is no Docker CLI-only package available in the
distribution repositories.

The client will be configured to use the local Unix socket in case Docker
Engine is installed with :ref:`debops.docker_server`. Otherwise it will be
configured to connect to the host in :envvar:`docker__docker_host` over HTTPS.
The CA, client certificate and private key are symlinked to /root/.docker/.

The ``docker-compose`` package is installed from the distribution repositories.
On Debian Stretch the backported variant is used for Docker Compose version 3
support.

To let the Docker daemon trust a private registry with self-signed
certificates, you can install the root CA used to sign the registry's
certificate on the Docker host through the :ref:`debops.pki` role.

This role does not support switching from Docker CE to Docker EE on an already
installed machine. The minimum supported Docker API version is 1.20.

Example inventory
-----------------

To configure Docker client on a given remote host, it needs to be added to the
``[debops_service_docker]`` Ansible inventory group:

.. code-block:: none

   [debops_service_docker]
   hostname

Example playbook
----------------

Here's an example playbook that can be used with this role:

.. literalinclude:: ../../../../ansible/playbooks/service/docker.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker:components``
  Run tasks related to Docker components (e.g. registry accounts, networks and
  containers).
