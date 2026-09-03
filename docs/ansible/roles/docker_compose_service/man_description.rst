.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Docker Compose`__ is a tool for defining and running multi-container
applications. The ``debops.docker_compose_service`` Ansible role can be used to
manage Docker Compose projects on hosts where Docker Engine is already installed
by the :ref:`debops.docker_server` role. The role deploys Compose files,
environment files and configuration files, then uses the
``community.docker.docker_compose_v2`` Ansible module to manage the project
lifecycle. It supports automatic :command:`nginx` reverse proxy configuration
through integration with the :ref:`debops.nginx` role.

.. __: https://docs.docker.com/compose/
