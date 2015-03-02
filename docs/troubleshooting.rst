Troubleshooting
===============

By default firewall does not allow access from any hosts for security reasons,
and no hosts are configured. You need to specify valid IP addresses or CIDR
ranges in :envvar:`nfs_allow` list which will configure access to the server in the
firewall. It will also automatically grant access to default NFS share to the
same IP addresses or CIDR ranges, using :envvar:`nfs_default_clients` list.

