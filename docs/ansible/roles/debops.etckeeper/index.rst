.. _debops.etckeeper:

debops.etckeeper
================

The ``debops.etckeeper`` Ansible role will install `etckeeper`__, which puts
the :file:`/etc` directory under version control. To do this,
:program:`etckeeper` hooks into the package management and from now on
automatically will commit changes to a local git repository under
:file:`/etc/.git/` directory. This makes it easy to see which changes are
applied on a specific host and quickly revert them, if something breaks.

.. __: https://etckeeper.branchable.com/

The role will install a special Ansible local fact which will commit any
changes in the :file:`/etc` directory as well, usually at the moment the
Ansible facts are gathered.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed


Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.etckeeper/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
