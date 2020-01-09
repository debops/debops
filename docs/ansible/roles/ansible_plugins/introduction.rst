Introduction
============

Ansible can be extended in various ways by the use of `custom plugins <https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html>`_.
This role contains a set of custom Ansible plugins used by various DebOps
roles. The plugins are enabled by including this role as a dependency of
another role.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.ansible_plugins

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
