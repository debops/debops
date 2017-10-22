Introduction
============

``debops-contrib.etckeeper`` will install etckeeper_ which puts :file:`/etc`
under version control. To do this it hooks into the package management and
from now on automatically commit changes to a local git repository under
:file:`/etc/.git`.

This makes it easy to see which changes are applied on a specific host and
quickly revert them, if something breaks.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run:

.. code-block:: console

    ansible-galaxy install debops-contrib.etckeeper

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:

.. _etckeeper: https://github.com/joeyh/etckeeper
