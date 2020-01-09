Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The ``debops.docker_gen`` role generates by default :program:`nginx` configuration,
based on `Romke van der Meulen blog entry <https://romkevandermeulen.nl/2015/02/19/docker-gen-automatic-nginx-config-with-a-human-touch.html>`_
Nginx upstreams defined this way can then be used in ``debops.nginx`` role to
automatically enable or disable upstream Docker containers in a given
configuration.

Due to how :program:`nginx` configuration works, upstreams need to be defined at the
start or reload of :program:`nginx` daemon, otherwise it will fail. And because of how
:command:`docker-gen` configuration works, it cannot generate the correct :program:`nginx`
configuration without Docker containers already present. Thus, the order of the
various things to be set up correctly is:

1. Create and start the Docker containers with environment variable
   ``NGINX_UPSTREAM`` specifying the wanted upstream name, for example::

       docker run -e NGINX_UPSTREAM=docker_upstream -d ...

2. Install and start :command:`docker-gen` will generate :program:`nginx` configuration
   with all Docker upstreams specified.

3. Install and start :program:`nginx` with templated configuration, and if upstream
   definitions are present, they will be immediately available and used.

When you are adding new services to :command:`docker-gen`, remember that at least one
needs to have ``-watch`` option enabled for the service to stay daemonized.

Useful variables
----------------

This is a list of role variables which your most likely want to define in
Ansible inventory to customize :command:`docker-gen`:

``docker_gen__remote``
  Enable support for remote Docker containers, accessed through Docker API over
  TLS.

``docker_gen__remote_host``
  Hostname or IP address of the remote Docker host. Without setting this remote
  connections are disabled.

Example inventory
-----------------

To configure :command:`docker-gen` on a given remote host, it need to be added to
``[debops_service_docker_gen]`` Ansible inventory group:

.. code-block:: none

   [debops_service_docker_gen]
   hostname

Example playbook
----------------

Here's an example playbook that can be used to manage :command:`docker-gen`:

.. literalinclude:: ../../../../ansible/playbooks/service/docker_gen.yml
   :language: yaml
