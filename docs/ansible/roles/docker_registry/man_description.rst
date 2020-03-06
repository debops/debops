.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.docker_registry`` Ansible role can be used to install and manage
a Docker Registry instance.
A `Docker Registry`__ is a service which allows you to publish and distribute
Docker container images. It can be used to create a private, local alternative
to a Docker Hub.

.. __: https://docs.docker.com/registry/

By default the role installs the Registry using an
OS package on supported OS releases; on older OS releases without the Registry
packaged in the repositories the role can download the official upstream
release from GitHub and build a Go :command:`docker-registry` binary
automatically.

The role integrates with the :ref:`debops.gitlab` and
:ref:`debops.redis_server` Ansible roles to provide backend support for the
`GitLab Container Registry`__ service. Docker Registry can be installed as
standalone service, in which case it will be secured using HTTP Basic
Authentication provided by the :ref:`debops.nginx` role.

.. __: https://gitlab.com/help/user/project/container_registry
