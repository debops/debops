.. _debops.authorized_keys:

debops.authorized_keys
======================

The ``debops.authorized_keys`` role can be used to manage SSH keys centrally in
the :file:`/etc/ssh/authorized_keys/` directory. The role only manages the keys
themselves, you should configure the ``sshd`` service to use them separately,
for example by using the :ref:`debops.sshd` Ansible role.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   upgrade

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/authorized_keys/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
