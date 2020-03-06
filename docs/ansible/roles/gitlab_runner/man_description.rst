.. Copyright (C) 2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`GitLab Runner <https://gitlab.com/gitlab-org/gitlab-ci-multi-runner>`_ is
a service written in Go which is used by the `GitLab CI <https://about.gitlab.com/gitlab-ci/>`_
to execute software builds on remote hosts. It supports builds executed by
local shell, over SSH or in a Docker containers.

The ``debops.gitlab_runner`` Ansible role will allow you to install and manage
GitLab Runner on Debian and Ubuntu hosts. You can use it to create multiple
Runner instances, each one with distinct configuration. The role will
automatically register the Runners in GitLab CI management host if a required
registration token is supplied.
