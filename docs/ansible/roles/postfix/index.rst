.. _debops.postfix:

debops.postfix
==============

The ``debops.postfix`` Ansible role can be used to install and manage
`Postfix`__, a SMTP server. It allows configuration of Postfix using Ansible
inventory variables, and provides a flexible API to the Postfix configuration
for other Ansible roles when it's used as a role dependency.

.. __: https://en.wikipedia.org/wiki/Postfix_%28software%29

.. toctree::
   :maxdepth: 3

   getting-started
   defaults/main
   defaults-detailed
   defaults-maincf
   defaults-mastercf
   dependency
   guides
   upgrade

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/postfix/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
