Introduction
============

The ``debops.authorized_keys`` role can be used to manage SSH keys centrally in
the ``/etc/ssh/authorized_keys/`` directory. The role only manages the keys
themselves, you should configure the ``sshd`` service to use them separately,
for example by using the ``debops.sshd`` Ansible role.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.authorized_keys

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
