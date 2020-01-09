Introduction
============

The ``debops.salt`` Ansible role can be used to install and configure
`SaltStack <https://saltstack.com/>`_ Master service. It is expected that Salt
Minions are installed using host deployment methods like PXE/preseeding, LXC
template scripts, etc. and contact the Salt Master service over DNS.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.salt

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
