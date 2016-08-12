Getting started
===============

Example Ansible inventory::

    [debops_nfs]
    data.example.org

Example playbook::

    ---

    - name: Manage NFS server
      hosts: debops_nfs

      roles:
        - role: debops.nfs
          tags: nfs

By default, role configures a NFS share located in ``/srv/nfs/`` directory,
however it won't be enabled automatically. To enable it, you need to specify
a list of IP addresses or CIDR networks which should have access to the share::

    nfs_allow: [ '192.0.2.0/24', '2002:db8::/64' ]

After that, you should be able to mount it on the client hosts in specified
network::

    mount -t nfs4 -o proto=tcp,port=2049,_netdev data.example.org:/srv/nfs /media/nfs

To configure the share in ``/etc/fstab`` using Ansible, you can use this
example playbook::

    ---
    - hosts: nfs_clients
      become: True

      tasks:

        - name: Mount NFS share
          mount:
            name: '/media/nfs'
            src: 'data.example.org:/srv/nfs'
            fstype: 'nfs4'
            opts: 'proto=tcp,port=2049,_netdev'
            state: 'mounted'

Currently in DebOps there's no support for Kerberos authentication, so by
default NFS role allows connections without authentication. When Kerberos
support is added, it will be required by default.

