Introduction
============

The ``debops.gitlab`` role can be used to install and manage a GitLab instance.
It supports automatic update of the currently installed version (when the role
is executed), as well as upgrade to a next stable GitLab release. You can deploy
the installation either on a single host, or a set of separate hosts, each one
with a different service (database, application, webserver).


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.gitlab

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
