Introduction
============

The ``debops.contrib-btrfs`` Ansible role allows you manage your Btrfs.
Currently the role supports management of Btrfs subvolumes.
More can be implemented as needed.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.9.0``. To install it, run::

    ansible-galaxy install debops.contrib-btrfs


This role requires the Ansible module ``btrfs_subvolume`` which is not yet
included in Ansible.
You can find it here: https://github.com/surpr1ze/ansible-btrfs-subvolume

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
