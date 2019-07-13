.. _debops.docker:

debops.docker
=============

`Docker`_ is a lightweight virtualization platform based on Linux kernel
features that allow creation and management of isolated application
environments.

.. _Docker: https://docker.com/

The ``debops.docker`` role is the "client" part - it installs the Docker CLI
Debian package from the upstream repository, and manages Docker components
through the Docker Ansible modules. You can use the :ref:`debops.docker_server`
role to manage the Docker host itself.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.docker/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
