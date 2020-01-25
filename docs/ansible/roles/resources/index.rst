.. _debops.resources:

debops.resources
================

This role allows management of custom file paths, file contents and archives on
remote hosts without the need to create a separate Ansible role. You can use
inventory lists to define what files to copy, what directories should exist on
a remote host, what online resources to download, and so on.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/resources/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
