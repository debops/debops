.. _rsyslog__unprivileged:

Unprivileged syslog and encrypted connections
=============================================

.. contents::
   :local:

The ``rsyslog`` daemon can be used in a privileged or an unprivileged mode. In
a privileged mode the daemon is run on the ``root`` account, has access to all
required files, sockets, etc. In the unprivileged mode, ``rsyslog`` daemon is
started in a privileged mode first, opens required sockets/ports and then drops
all of its privileges and supplementary UNIX groups.

The ``debops.rsyslog`` role allows you to select which mode is used by
configuring the :envvar:`rsyslog__unprivileged` boolean variable. By default, to
preserve original configuration, the role enables unprivileged mode on Ubuntu
hosts, leaving the configuration privileged on Debian hosts.

The unprivileged operation places certain restrictions on the system
configuration. In particular, the ``rsyslog`` process only uses its primary
system group, dropping any additional groups the user is in. This means, that
using TLS with the default configuration maintained by :ref:`debops.pki` role
becomes problematic - unprivileged ``rsyslog`` process uses only its own
primary group, so it cannot access private keys to allow encrypted connections.

There are multiple solutions to this problem, which you can use. Each one has
pros and cons, and you should evaluate the selected method in a development
environment before implementing it in production to avoid issues.

Run the daemon in privileged mode
---------------------------------

This method is the default on Debian hosts. Ubuntu hosts use the unprivileged
mode by default, and reverting to the privileged mode should work, but that
hasn't been evaluated yet.

The daemon will be run with the ``root`` permissions, and there shouldn't be
any issues with file access. Enabling TLS connections should work out of the
box. On the downside, an externally accessible service is running with ``root``
permissions, so you should be careful what hosts have access to it, this is
controlled using the firewall.

To enable this mode, set the following in the Ansible inventory:

.. code-block:: yaml

   rsyslog__unprivileged: False

This will enforce the privileged operation.

Grant access to private keys by additional groups
-------------------------------------------------

The :ref:`debops.pki` role that maintains the DebOps X.509 infrastructure, allows
you to specify additional system groups, which should have access to the
private keys. This should be configured before the role creates the private
keys, because the permissions are not enforced afterwards - this means that you
will need to recreate the private keys and certificates, or update the
permissions manually. Additional permissions are granted using the filesystem
ACL support.

To enable ``rsyslog`` to get access to the private keys in unprivileged mode by
the ``syslog`` system groups, configure in the Ansible inventory:

.. code-block:: yaml

   # Ensure that needed system group is present
   pki_private_groups_present:
     - name: 'syslog'
       system: True

   # Add custom ACL groups to private files and directories for all PKI realms
   pki_private_dir_acl_groups:  [ 'syslog' ]
   pki_private_file_acl_groups: [ 'syslog' ]

   # Or, add custom ACL groups to private files only in default PKI realm
   pki_default_realms:
     - name: 'domain'
       acme: False
       private_dir_acl_groups:  [ 'syslog' ]
       private_file_acl_groups: [ 'syslog' ]

After the PKI realm is recreated, you can check the result using command:

.. code-block:: console

   root@logs:~# getfacl /etc/pki/realms/domain/private
   root@logs:~# getfacl /etc/pki/realms/domain/private/key.pem

You should see the ``syslog`` entry on the list of groups that can access the
respective files and directories. When the ``rsyslog`` process is restarted, it
should be able to access the private keys without issues. To enable the
unprivileged mode on Debian hosts, you might want to enforce it through the
Ansible inventory. Here it is, with example log forwarding to remote host with
TCP over TLS:

.. code-block:: yaml

   # Enable unprivileged operation
   rsyslog__unprivileged: True

   # Enable TLS support
   rsyslog__capabilities: [ 'tls' ]

   # Forward logs over encrypted TCP connection
   rsyslog__forward: [ '*.* @@logs.{{ ansible_domain }}:6514' ]

Create custom PKI realm for syslog
----------------------------------

The :ref:`debops.pki` role allows you to create multiple PKI realms with different
purposes and configuration. If you don't want to modify and existing
infrastructure in place, creating a separate internal realm just for syslog
might be an easy alternative.

To create new PKI realm, add this to the Ansible inventory for all involved
hosts:

.. code-block:: yaml

   # Ensure that needed system group is present
   pki_private_groups_present:
     - name: 'syslog'
       system: True

   # Create custom realm for syslog
   pki_realms:
     - name: 'syslog'
       acme: False
       private_dir_group:  'syslog'
       private_file_group: 'syslog'

When the new PKI realm is created, the private directory and files inside
should be owned by the ``syslog`` group. This should ensure that the
``rsyslog`` daemon in the unprivileged mode, running as ``syslog`` user, should
have access to them. The certificates should be signed by existing
:ref:`debops.pki` Certificate Authority, so they should be trusted by all hosts in
the cluster.

When the new PKI realm is ready, you can tell ``debops.rsyslog`` role to use it:

.. code-block:: yaml

   # Enable unprivileged operation
   rsyslog__unprivileged: True

   # Enable TLS support
   rsyslog__capabilities: [ 'tls' ]

   # Change the default PKI realm used by rsyslog
   rsyslog__pki_realm: 'syslog'

   # Forward logs over encrypted TCP connection
   rsyslog__forward: [ '*.* @@logs.{{ ansible_domain }}:6514' ]

When the new configuration is applied, you should see in the ``rsyslog``
configuration files that the daemon is using the correct private key and
certificate.

Testing encrypted connections
-----------------------------

To make sure that the logs are sent over an encrypted connection, you can check
the traffic using the ``tshark`` command. On the receiving server, run the
command:

.. code-block:: console

   root@logs:~# tshark -i eth0 -f "dst port 514 or dst port 6514" \
                -d tcp.port==514,syslog -d tcp.port==6514,syslog

This will output packets that are sent to TCP ports 514 (plaintext traffic) and
6514 (TLS traffic). Afterwards, on remote hosts try sending some test log
messages:

.. code-block:: console

   user@host:~$ logger Test log message, please ignore

If the connection is not encrypted, you should see something similar to this
(notice the unencrypted contents of the packet)::

    9 132.751792 192.0.2.2 -> 192.0.2.1 Syslog 133 USER.NOTICE: May 16 14:06:05 host user: Test log message, please ignore\n

If the connection is encrypted, output should look similar to this::

    9 132.751792 192.0.2.2 -> 192.0.2.1 Syslog 164 \027\003\003\000]\000\000\000\000\000\000\000\037\257\301,\030\365\311\324\023qR9\b\352\203\256\306\260T\023\022\016g\271\220\325\031\250\326\323\0045\3549\270\277>\205\301\256\325\234\246\tzt\333\255\002\006K"\254\334\021wB1\353\f\356,u\344\220\207d\024o\305\234\b\201\003Js[\2533\261\207\231?k\230J

Of course, the contents of the logs should appear normally in the log files,
for example in :file:`/var/log/remote/hosts/host/syslog` you should see::

    May 16 14:06:05 host user: Test log message, please ignore
