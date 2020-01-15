.. _owncloud__ref_external_storage:

External storage
================

This section gives some hints how to setup external storage for ownCloud.
The automation support for this in ``debops.owncloud`` currently limited. This
might be added in a later version of the role.

SMB/CIFS
--------

To enable SMB/CIFS support in the role set:

.. code-block:: none

   owncloud__smb_support: True

in your inventory.

Setting up SMB/CIFS in different environment based on Debian Jessie required
some debugging so if you have trouble with SMB and MS Windows or NetApp file
servers, you can try the following.

Add the host(s) to the ``debops_service_samba`` Ansible host group:

.. code-block:: none

    [debops_service_samba]
    hostname

and include this:

.. code-block:: yaml

   # Don’t install the ``samba`` server as it is not needed on a typical
   # ownCloud server which acts as SMB client.
   samba__base_packages:
     # - 'samba'
     - 'samba-common'
     - 'samba-common-bin'

   # Set AD domain. It might be required to adjust in case `netbase__domain`
   # is not equal to the Samba domain/workgroup.
   # ownCloud as of 9.0 provides a Domain field when setting up an external
   # storage but configuring this here is still nice in case you need to debug
   # a SMB/CIFS share using `smbclient`.
   samba__workgroup: '{{ netbase__domain }}'

   samba__global_custom:
     ## DFS workaround:
     'client ntlmv2 auth': 'no'

     ## Downgrade NetApp workaround:
     ## https://community.netapp.com/t5/Network-Storage-Protocols-Discussions/samba-3-6-23-30-on-CentOS-gt-error-in-smbclient/m-p/118486#M8350
     'client use spnego': 'no'

in your inventory to get started.

The run the ``service/samba`` playbook.

When you have further suggestions, you are welcome to share them here to save
us all some debugging time.
