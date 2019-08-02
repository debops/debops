.. _examples_index:

Debops examples index
=====================

Aim of examples
---------------

DebOps examples are DebOps projects that contain only inventory files.
They are provided to DebOps users to:

- describe a specific configuration (scenario): recipes
- use as integration tests


Design of examples
------------------

Examples are written and tested in Vagrant environment used in
DebOps. Each example directory contain a Vagrantfile that can be use to start
VMs in this directory.

To simplify provisioning and to leverage auto-generated Ansible inventory in
Vagrant environement, examples use only groups in inventory (instead of
hosts).


Provisioning examples in Vagrant
--------------------------------

After doing a :cmd:`vagrant up` in an example directory, you can provision
examples with following command:

..  code-block:: console

    vagrant provision --provision-with=setup_examples

If you modified your examples directory in your git repo and want to get
latest examples in your vagrant environment, you willl need to run:

.. code-block:: console

   vagrant rsync
   vagrant provision --provision-with=setup_examples

.. toctree::
   :maxdepth: 1
   :glob:

   */index

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
