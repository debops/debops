.. _debops.debops_fact:

debops.debops_fact
==================

The ``debops.debops_fact`` Ansible role can be used to read JSON data from
a set of INI configuration files and make them available as Ansible local
facts. This mechanism can be used to maintain common facts between separate
Ansible roles without the need for them to know about the specific file
structures, using ``ini_file`` Ansible module.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops_fact/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
