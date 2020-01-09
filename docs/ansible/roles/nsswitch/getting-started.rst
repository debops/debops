Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The ``debops.nsswitch`` role is designed to allow control over the
:file:`/etc/nsswitch.conf` configuration file both by other Ansible roles (as
a role dependency) and by the system administrator. The Ansible roles can
enable different NSS services after they have been configured on the host. The
system administrator can decide what order the various NSS services should be
used in and if they should be used in a particular NSS database lookup.

The default role configuration shouldn't affect the :file:`/etc/nsswitch.conf`
configuration file provided by the OS distribution, apart from changing the
mDNS service from IPv4 to both IPv6 and IPv4 (see :ref:`nsswitch__ref_mdns` for
more details). The convention on Debian is that different packages which
provide NSS services modify the :file:`/etc/nsswitch.conf` configuration file
themselves, therefore the role tries to respect local modifications. A set of
various NSS services (LDAP, SSS, Winbind) should be detected and enabled
accordingly, however the order of the services comes from the role itself and
might change from the one created by the Debian packages.

According to the :man:`nsswitch.conf(5)`, processes that use the NSS
configuration file read the :file:`/etc/nsswitch.conf` only once, therefore
a restart of these processes (for example :command:`nscd` or :command:`sssd`)
might be needed.

At the moment the role restarts the :command:`systemd-logind` service on the
configuration changes, but only when the playbook is executed against a remote
host, to avoid breaking local user session. Changes on ``localhost`` might need
the system to be restarted for :command:`systemd-logind` to reload the new
configuration correctly.


.. _nsswitch__ref_mdns:

mDNS (Avahi/ZeroConf) support
-----------------------------

The role will replace the ``mdns4_minimal`` NSS service with ``mdns_minimal``
if the IPv6 support is enabled in the ``debops.avahi`` Ansible role (detected
via Ansible local facts). This will allow lookup of the ``.local`` domain over
IPv6 network.

To disable this behaviour, set in the inventory:

.. code-block:: yaml

   nsswitch__database_map:
     'hosts':
       - 'files'
       - [ 'mdns4_minimal', '[NOTFOUND=return]' ]
       - 'dns'
       - 'wins'

Use of the ``mdns4_minimal`` NSS service is currently an upstream default
behaviour, which `was suggested for Debian in 2008 <https://bugs.debian.org/466014>`_.
However the IPv6 deployment was not very widespread at the time, which is not
true anymore. Because DebOps tries to be IPv6-friendly and work out of the box
with IPv6 network, the role by default will enable mDNS support on IPv6.
If this becomes problematic, the default might change to leaving
``mdns4_minimal`` in its current state.


Example inventory
-----------------

The ``debops.nsswitch`` role is part of the common DebOps playbook. You don't
need to do anything to enable it on all hosts.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nsswitch`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nsswitch.yml
   :language: yaml
