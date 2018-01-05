Introduction
============

The ``debops.apt_install`` Ansible role is meant to be used as an easy way to
install APT packages on hosts that don't require more extensive configuration
which would require a more extensive, custom Ansible role. The role itself
exposes several Ansible default variables which can be used to specify custom
lists of packages on different levels of Ansible inventory (global, per-group
or per-host).

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.apt_install

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
