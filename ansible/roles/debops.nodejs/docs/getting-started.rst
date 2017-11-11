Getting started
===============

NPM is installed from source
----------------------------

The ``npm`` package has been removed from Debian Stable (currently Stretch).
The :command:`npm` command is supported natively by the upstream ``.deb``
packages, however when upstream is not enabled, role will now by default
install the NPM support using the project's :command:`git` repository.

You can read more details about the NPM removal from Debian here:
http://www.grulic.org.ar/~mdione/glob/posts/installing-npm-on-debian-testing/


Example inventory
-----------------

To configure a NodeJS environment on a given host or set of hosts, they need to
be added to ``[debops_service_nodejs]`` Ansible group in the inventory:

.. code-block:: none

   [debops_service_nodejs]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nodejs`` role:

.. literalinclude:: playbooks/nodejs.yml
   :language: yaml
