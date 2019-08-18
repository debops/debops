.. _debops.docker_server:

debops.docker_server
====================

`Docker`_ is a lightweight virtualization platform based on Linux kernel
features that allow creation and management of isolated application
environments.

.. _Docker: https://docker.com/

The ``debops.docker_server`` role can be used to install and configure Docker
service on Debian/Ubuntu hosts. To role supports installation of Docker from OS
distribution repositories, as well as from the upstream repository.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   docker-virtualenv

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.docker_server/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
