Getting started
===============


NodeJS and NPM from Debian Backports
------------------------------------

On a given Debian Oldstable release, the role will install the ``nodejs`` and
``npm`` packages from the backports repository of the same OS release to ensure
feature parity between the Oldstable and Stable Debian releases. This means
that, for example, on Debian Stretch the role will use the Node.js and NPM
packages from the ``stretch-backports`` repository instead of the OS release
repository.

Newer Node.js and NPM packages can be installed using the NodeSource
repository, which can be enabled using the :envvar:`nodejs__node_upstream`
variable.


Example inventory
-----------------

To configure a Node.js environment on a given host or set of hosts, they need
to be added to ``[debops_service_nodejs]`` Ansible group in the inventory:

.. code-block:: none

   [debops_service_nodejs]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nodejs`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nodejs.yml
   :language: yaml
