.. _debops.debops_legacy:

debops.debops_legacy
====================

The ``debops.debops_legacy`` Ansible role can be used to clean up legacy files,
directories, APT packages or :command:`dpkg-divert` diversions created by
DebOps but no longer used.

The role is not included in the main DebOps playbook to not cause data
destruction by mistake. You are advised to use it with caution - it will
destroy data on your DebOps hosts. To check the changes that will be done
before implementing them, you can run the role against DebOps hosts with:

.. code-block:: console

   debops service/debops_legacy -l <host> --diff --check

Any changes that the role will create on the hosts can be overridden via the
Ansible inventory if needed.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.debops_legacy/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
