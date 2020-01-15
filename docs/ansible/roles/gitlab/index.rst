.. _debops.gitlab:

debops.gitlab
=============

The ``debops.gitlab`` role can be used to install and manage a GitLab instance.
It supports automatic update of the currently installed version (when the role
is executed), as well as upgrade to a next stable GitLab release. You can deploy
the installation either on a single host, or a set of separate hosts, each one
with a different service (database, application, webserver).

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   remote_db
   ldap-dit

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/gitlab/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
