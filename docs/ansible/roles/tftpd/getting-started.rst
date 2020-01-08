Getting started
===============

.. contents::
   :local:

Usage from TFTP clients
-----------------------

If you try to check if the TFTP server works using a TFTP client, ensure that
the client host can receive UDP packets on port 69 (tftp). This port might be
blocked by the firewall on the client side.


Conditional write access
------------------------

If the :envvar:`tftpd__allow` variable is defined to limit the access to the
TFTP service to specific subnets, the role will automatically enable write
access in the :command:`tftpd-hpa` service. The
:envvar:`tftpd__upload_directory` defines the name of the directory in the TFTP
root directory which will be created by the role to allow file uploads.


Example inventory
-----------------

To configure a TFTP server on a host, you should add it to the
``[debops_service_tftpd]`` Ansible inventory group:

.. code-block:: none

   [debops_service_tftpd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.tftpd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/tftpd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::tftpd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.tftpd`` Ansible role:

- Manual pages: :man:`tftpd-hpa/in.tftpd(8)`
