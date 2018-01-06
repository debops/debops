Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To configure a TFTP server on a host, you should add it to the
``[debops_tftpd]`` group::

    [debops_tftpd]
    hostname


Example playbook
----------------

Here's an example playbook which uses ``debops.tftpd`` role::

    ---

    - name: Configure standalone TFTP server
      hosts: debops_tftpd

      roles:
        - role: debops.tftpd
          tags: tftpd

