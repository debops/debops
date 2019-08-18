Introduction
============

The ``debops.environment`` role can be used to manage system-wide environment
variables, by default located in ``/etc/environment`` file. Variables are
gathered from multiple sources and combined to allow global/group/host tiered
environment modeled after Ansible inventory.

This role can also be used by other Ansible roles as a dependency to create
global environment variables in a safe way, that preserves idempotency.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.environment

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
