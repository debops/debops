Introduction
============

.. include:: ../../../includes/global.rst

The ``debops.postfix`` Ansible role can be used to install and manage
`Postfix`_, a SMTP server. It allows configuration of Postfix using Ansible
inventory variables, and provides a flexible API to the Postfix configuration
for other Ansible roles when it's used as a role dependency.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.postfix
..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
