.. _debops.hashicorp:

debops.hashicorp
================

The ``debops.hashicorp`` Ansible role can be used to securely install HashiCorp__
applications, such as `Consul`__, `Terraform`__, `Vault`__ and others.

The selected applications are downloaded from the HashiCorp release repository,
authenticated using the HashiCorp OpenPGP key and installed on the system.
After that, other Ansible roles can be used to configure them as needed.

.. __: https://en.wikipedia.org/wiki/HashiCorp
.. __: https://consul.io/
.. __: https://terraform.io/
.. __: https://vaultproject.io/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   security
   ansible-integration

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/hashicorp/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
