Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To enable swap files on a host, it needs to be added to ``[debops_swapfile]``
Ansible group in inventory::

    [debops_swapfile]
    hostname

Default configuration will create a 512 MB ``/swapfile`` and will make sure
that it's added in ``/etc/fstab``.

Example playbook
----------------

Here's an example playbook you can use to configure swap on a host::

    ---
    - name: Manage swap
      hosts: 'debops_swapfile'
      become: True

      roles:

        - role: debops.swapfile

