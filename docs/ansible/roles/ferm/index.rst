.. _debops.ferm:

debops.ferm
===========

`ferm`_ is a wrapper around the :command:`iptables` and the :command:`ip6tables` commands which lets
you manage host firewalls in an easy and Ansible-friendly way. This role can
be used to setup firewall rules directly from the inventory, or it can be used
as a dependency by other roles to setup firewall rules for other services.

.. _ferm: http://ferm.foo-projects.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   rules
   guides

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/ferm/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
