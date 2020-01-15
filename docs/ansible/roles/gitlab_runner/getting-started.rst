Getting started
===============

.. contents::
   :local:

.. _gitlab_runner__token:

GitLab CI registration token
----------------------------

To register a Runner with your GitLab CI instance, you need to provide
a registration token. It can be found on the ``https://<host>/admin/runners``
page of your GitLab installation.

The registration token is generated randomly on each GitLab startup, and
unfortunately cannot be accessed using an API. Therefore, the easiest way to
provide it to the role is to store it in an environment variable. The
``debops.gitlab_runner`` checks the value ofthe ``$GITLAB_RUNNER_TOKEN`` system
variable and uses the token found there.

The registration token is required to perform changes on the GitLab server
itself, ie. registration and removal of Runners. It's not required for the role
to manage the Runners on the host - the Runner tokens are saved in local
Ansible facts and reused if necessary.

An example way to run ``debops`` so that the role registers the Runners in
GitLab CI:

.. code-block:: console

   GITLAB_RUNNER_TOKEN=<random-token> debops service/gitlab_runner

To change the environment variable that holds the registration token, or save
the token in Ansible inventory, you can use the :envvar:`gitlab_runner__token`
variable.

In case that you don't want to expose the registration token via the Ansible
inventory directly, you can store it it in the
:file:`ansible/secret/credentials/` directory managed by the
:ref:`debops.secret` role in a predetermined location.

To create the path and file to store the GitLab Token execute this commands in
the root of the DebOps project directory with the relevant GitLab domain:

.. code-block:: console

   mkdir -pv ansible/secret/credentials/code.example.org/gitlab/runner
   editor ansible/secret/credentials/code.example.org/gitlab/runner/token

In the editor, paste the GitLab registration token and save the file. Then add
the :envvar:`gitlab_runner__token` variable to your inventory.

.. code-block:: console

   gitlab_runner__token: '{{ lookup("password", secret
                           + "/credentials/" + gitlab_runner__api_fqdn
                           + "/gitlab/runner/token chars=ascii,numbers") }}'

This allows the token to be safely stored outside of the inventory but
accessible at runtime.


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
