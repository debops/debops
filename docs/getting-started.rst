Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To enable swap files on a host, it needs to be added to the
``[debops_service_swapfile]`` group in Ansible’s inventory::

    [debops_service_swapfile]
    hostname

The default configuration will create a 512 MB :file:`/swapfile` and will make sure
that it's added in :file:`/etc/fstab`.

Example playbook
----------------

Here's an example playbook you can use to configure swap on a host::

    ---
    - name: Manage swap
      hosts: 'debops_service_swapfile'
      become: True

      roles:

        - role: debops.swapfile

