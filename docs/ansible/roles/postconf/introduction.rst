Introduction
============

The ``debops.postconf`` Ansible role configures Postfix SMTP server according
to autodetected or manually selected parameters. The role uses the
:ref:`debops.postfix` Ansible role to manage Postfix configuration files and lookup
tables.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.postconf

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
