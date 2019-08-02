Getting started
===============


NodeJS and NPM from Debian Backports
------------------------------------

On a given Debian Oldstable release, the role will install the ``nodejs`` and
``npm`` packages from the backports repository of the same OS release to ensure
feature parity between the Oldstable and Stable Debian releases. This means
that, for example, on Debian Stretch the role will use the NodeJS and NPM
packages from the ``stretch-backports`` repository instead of the OS release
repository.

Newer NodeJS and NPM packages can be installed using the NodeSource repository,
which can be enabled using the :envvar:`nodejs__node_upstream` variable.


Support for Yarn package manager
--------------------------------

The ``debops.nodejs`` role can install Yarn package manager from its upstream
APT repository. By default this is disabled; to enable Yarn installation, you
need to set the ``nodejs__yarn_upstream`` variable to ``True``.


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

.. literalinclude:: ../../../../ansible/playbooks/service/nodejs.yml
   :language: yaml
