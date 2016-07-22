Introduction
============

The ``debops.hashicorp`` Ansible role can be used to securely install
`HashiCorp <https://hashicorp.com/>`_ applications, such as
`Consul <https://consul.io/>`_, `Terraform <https://terraform.io/>`_,
`Vault <https://vaultproject.io/>`_ and others.

The selected applications are downloaded from the hashiCorp release repository,
authenticated using the HashiCorp OpenPGP key and installed on the system.
After that, other Ansible roles can be used to configure them as needed.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.hashicorp

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
