Example eduroam setup
=====================


This is an example basic `eduroam`__ configuration for the
:ref:`debops.freeradius` Ansible role.

.. __: https://en.wikipedia.org/wiki/Eduroam

.. note:: The files are available in the DebOps monorepo, as separate YAML
   files in the :file:`docs/ansible/roles/debops.freeradius/examples/eduroam/`
   directory.

You can put these files in the Ansible inventory, in
:file:`ansible/inventory/host_vars/<hostname>/` directory. After doing this and
tweaking the configuration you should run the :ref:`debops.freeradius` and
:ref:`debops.resources` Ansible roles against the host.

This configuration is based on the example `eduroam configuration guide`__ on
the FreeRADIUS Wiki. You should check this page for detailed guide about this
setup.

.. __: https://wiki.freeradius.org/guide/eduroam


FreeRADIUS configuration
------------------------

.. literalinclude:: examples/eduroam/freeradius.yml
   :language: yaml


Additional resources
--------------------

The :file:`install-eapol_test` script created by this configuration can be used
to install the :command:`eapol_test` command on either the same host as the
FreeRADIUS server, or on a different, remote host, to test the connectivity
over the network.

.. literalinclude:: examples/eduroam/resources.yml
   :language: yaml
