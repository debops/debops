.. _docker_server__ref_virtualenv:

Docker virtualenv support
=========================

.. contents::
   :local:
   :depth: 1


Python and Docker relationship
------------------------------

Docker can be expanded or managed by a few additional Python-based tools. The
company behind Docker provides a :command:`docker-compose` Python script which
can be used to manage multiple Docker containers at a time. Ansible provides
a few Docker-related modules as well. Therefore a correctly configured Python
environment is very useful on a Docker host.

The ``debops.docker_server`` Ansible role maintains a separate Python
:command:`virtualenv` environment just for Docker-related Python packages. This
is done so that Python modules used by upstream Docker, don't affect the host
Python environment. The Docker :command:`virtualenv` environment is by default
located in the :file:`/usr/local/lib/docker/virtualenv/` directory but it can
be changed if needed.

The :command:`docker-compose` script will be symlinked in the host environment,
in :file:`/usr/local/bin/docker-compose`, so that the command can be used from
the host's shell.

The Python interpreter located in the Docker :command:`virtualenv` environment
will be exposed in the host environment as
:file:`/usr/local/bin/docker-python`. That way you can use it in the Python
scripts executed in the host environment. To use the Docker Python interpreter
in a script, define it's shebang line as:

.. code-block:: python

   #!/usr/bin/env docker-python


Ansible modules and Docker virtualenv
-------------------------------------

The default host does not have any Docker-related Python modules available,
therefore Ansible modules that interact with Docker, like ``docker``,
``docker_container``, ``docker_image``, etc. will not work out of the box in
normal Ansible playbooks and roles. To solve that, you can use the
``ansible_python_interpreter`` variable defined at the playbook level. Playbook
variables cannot be templated by Jinja, therefore a static value must be used,
and relates to the :command:`docker-python` command exposed earlier.

Here's an example playbook that uses a Python interpreter from the Docker
:command:`virtualenv` environment:

.. literalinclude:: examples/docker-redis.yml
   :language: yaml

Keep in mind that more extensive playbooks that use Ansible roles or modules
other than the Docker-related ones might need to be executed in their own
separate plays, to use the host Python interpreter instead of the one
maintained in the Docker :command:`virtualenv` environment. Alternatively, you
need to ensure that the Docker :command:`virtualenv` environment contains all
needed Python modules.


How to access the Docker virtualenv
-----------------------------------

To enter the Docker :command:`virtualenv` environment on a host, execute the
commands on the ``root`` account:

.. code-block:: console

   cd /usr/local/lib/docker/virtualenv
   source bin/activate

After that you can execute usual :command:`pip` commands to manage Python
packages inside the environment.
