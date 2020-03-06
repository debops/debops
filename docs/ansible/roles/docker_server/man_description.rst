.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Imre Jonk <mail@imrejonk.nl>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Docker`_ is a lightweight virtualization platform based on Linux kernel
features that allow creation and management of isolated application
environments. This role can be used to set up a Docker host. It installs the
container runtime and makes sure that ferm does not interfere with the iptables
rules set by Docker. ``debops.docker_server`` does not manage containers
itself, for that you can use the :ref:`debops.docker` role.

.. _Docker: https://docker.com/

The ``debops.docker_server`` role can be used to install and configure Docker
service on Debian/Ubuntu hosts. To role supports installation of Docker from OS
distribution repositories, as well as from the upstream repository.
