.. _debops.mailman:

debops.mailman
==============

The :ref:`debops.mailman` Ansible role can be used to create and manage mailing
lists using `GNU Mailman <http://list.org/>`_ package.

By default the role provides configuration for :ref:`debops.postfix` role to
configure the SMTP server integration, as well as :ref:`debops.nginx` role to
configure access to the web control panel.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/mailman/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
