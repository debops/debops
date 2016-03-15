Introduction
============

etckeeper__ makes it easy to put :file:`/etc`
under version control by hooking into the package management systems and
automatically committing changes. This makes it easy to see which changes
are applied on a specific host and quickly revert them, if something
breaks.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run::

    ansible-galaxy install debops.contrib-etckeeper

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:

.. _etckeeper: https://github.com/joeyh/etckeeper
