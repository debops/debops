Introduction
============

The ``debops.debops_fact`` Ansible role can be used to read JSON data from
a set of INI configuration files and make them available as Ansible local
facts. This mechanism can be used to maintain common facts between separate
Ansible roles without the need for them to know about the specific file
structures, using ``ini_file`` Ansible module.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.debops_fact

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
