.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Docker`__ is a platform for running applications in lightweight, isolated
containers. The ``debops.docker_service`` Ansible role can be used to manage
simple Docker container services on hosts where Docker Engine is already
installed by the :ref:`debops.docker_server` role. The role supports port
mapping, volume mounts, environment variables, resource limits and automatic
:command:`nginx` reverse proxy configuration through integration with the
:ref:`debops.nginx` role.

.. __: https://www.docker.com/
