.. Copyright (C) 2016-2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

.. _gitlab_runner__token:

GitLab CI registration token
----------------------------

To register a Runner with your GitLab CI instance, you need to provide
a `personal API access token`__. It can be generated using the profile
preferences of your GitLab user account.

.. __: https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html

Personal API access tokens are created for specific GitLab user accounts and
shouldn't be shared in the Ansible inventory or secrets managed by the
:ref:`debops.secret` Ansible role. The :ref:`debops.gitlab_runner` role checks
the ``$GITLAB_API_TOKEN`` environment variable on the Ansible Controller to get
the token string and use it for registration.

For convenience, the token can be stored in the :file:`.env` configuration file
at the root of the DebOps project directory, which uses the ``dotenv`` format.
Variables defined in this file will be automatically sourced in the execution
environment when the :command:`debops` script is invoked.  Users can check the
runtime environment by executing the command:

.. code-block:: console

   debops env

The :file:`.env` file is ignored by :command:`git` and shouldn't be committed
into the project's version control.

To change the environment variable that holds the API access token, or save
the token in Ansible inventory, you can use the :envvar:`gitlab_runner__api_token`
variable.


Initial configuration
---------------------

By default, ``debops.gitlab_runner`` will configure a single Runner instance
which uses a shell executor. If a Docker installation is detected via Ansible
local facts, the role will disable the shell executor and configure two Docker
executors - one unprivileged, and one privileged. The executors will have a set
of tags that identify them, shell executors will have additional tags that
describe the host's architecture, OS release, etc.

If the ``debops.lxc`` role has been used to configure LXC support on the host,
the ``debops.gitlab_runner`` will install the ``vagrant-lxc`` package and
configure :command:`sudo` support for it. Using a shell executor you can start
and stop Vagrant Boxes using LXC containers and execute commands inside them.

If the ``debops.libvirtd`` role has been used to configure libvirt support on
the host, the ``debops.gitlab_runner`` will install the ``vagrant-libvirt``
package and configure :command:`sudo` support for it. Using a shell executor
you can start and stop Vagrant Boxes using libvirt and execute commands inside
them.

The Runner instances can be configured with variables specified as the keys of
the dictionary that holds the specific Runner configuration. If any required
keys are not specified, the value of the global variable will be used instead.

Some of the variables will be added together (Docker volumes, for example), so
that you can define a list of global values included in all of the Runner
instances.

.. _gitlab_runner__environment:

Environment variables
---------------------

You can use :envvar:`gitlab_runner__environment` default variable to specify a custom
set of environment variables to configure in a GitLab Runner instance. You can
use the global variable, or set the environment at the instance level by
specifying it as ``item.environment`` variable.

The environment variables can be specified in a different ways:

- a single variable as a string:

  .. code-block:: yaml

     gitlab_runner__environment: 'VARIABLE=value'


- a list of environment variables:

  .. code-block:: yaml

     gitlab_runner__environment:
       - 'VARIABLE1=value1'
       - 'VARIABLE2=value2'


- a YAML dictionary with variable names as keys and their values as values:

  .. code-block:: yaml

     gitlab_runner__environment:
       VARIABLE1: 'value1'
       VARIABLE2: 'value2'


Different specifications cannot be mixed together.


Example inventory
-----------------

To install GitLab Runner service on a host, it needs to be added to the
``[debops_service_gitlab_runner]`` inventory host group:

.. code-block:: none

   [debops_service_gitlab_runner]
   hostname


Example playbook
----------------

Here's an example playbook that can be used to enable and manage the GitLab
Runner service on a set of hosts:

.. literalinclude:: ../../../../ansible/playbooks/service/gitlab_runner.yml
   :language: yaml
   :lines: 1,5-
