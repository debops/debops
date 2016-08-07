Introduction
============

The ``debops.debops_fact`` Ansible role maintains a persistent key/value JSON
database using Ansible local facts. This mechanism can be used through the
Ansible inventory or role dependent variables to pass data between Ansible
roles. Using an intermediary role, separate Ansible roles don't need to know
about the data structures used by each other, only a common interface defined
by ``debops.debops_fact`` role.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.debops_fact

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
