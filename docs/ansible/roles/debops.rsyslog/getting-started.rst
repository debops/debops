Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The ``debops.rsyslog`` default configuration is designed to closely resemble
the Debian ``rsyslog`` package defaults. The same system logs will be
generated, although with slightly longer log rotation. If the operating system
is Debian, ``rsyslog`` will be run on a privileged ``root`` account; if the
system is Ubuntu, an unprivileged ``syslog`` account will be used by default.

The ``rsyslog`` configuration is stored in :file:`/etc/rsyslog.d/`, most of the
configuration located in :file:`/etc/rsyslog.conf` has been moved to the directory
and put in separate files (old configuration is preserved in a diverted file).

Configuration filename extensions
---------------------------------

The configuration order is important, and to aid support of configuration from
other roles, ``debops.rsyslog`` includes configuration files with different
filename extensions at certain parts of the configuration:

:file:`/etc/rsyslog.d/*.conf`
  These files are included by default. They are meant to be used for
  configuration of the local system logs, the extension is used to preserve
  compatibility with Debian package conventions.

:file:`/etc/rsyslog.d/*.template`
  These configuration files can be used to create custom templates used by
  ``rsyslog`` in different parts of the configuration.

:file:`/etc/rsyslog.d/*.system`
  These configuration files are meant to be used to define log matching rules
  specific to a given system, to store logs in different files.

:file:`/etc/rsyslog.d/*.remote`
  These configuration files are meant to store configuration for logs coming
  from other systems over the network. These rules will be defined in
  a separate "ruleset" called ``remote`` which is used by the UDP and TCP input
  modules. This way the local (system) logs and remote logs from other hosts
  can be managed separately and shouldn't mix with each other.

Quick start: log forwarding
---------------------------

To enable log forwarding, you will want to configure a few variables differently
in your Ansible inventory. The quick and dirty setup described here assumes
that you want to forward logs over UDP without any encryption, so it should
only be used for testing if remote logs work. For more advanced configuration
check the :ref:`rsyslog__forward` documentation.

First, on the host that should receive the remote logs, for example in
:file:`ansible/inventory/host_vars/logs.example.org/rsyslog.yml`, configure
variables:

.. code-block:: yaml

   # Enable network input channels and storage of remote logs in filesystem
   rsyslog__capabilities: [ 'network', 'remote-files' ]

   # Specify which subnets can send remote logs through the firewall
   rsyslog__host_allow: [ '192.0.2.0/24', '2001:db8::/32' ]

   # Mask log forwarding configuration defined elsewhere
   rsyslog__forward: []
   rsyslog__group_forward: []
   rsyslog__host_forward: []

   # Or, alternatively, forward logs to a different host
   rsyslog__host_forward: [ '*.* @other.{{ ansible_domain }}' ]

This will prepare a given central log storage host to receive logs from other
systems on specified subnets, and store them in :file:`/var/log/remote/` directory.

Now, you can enable log forwarding for all hosts in your inventory (in
:file:`ansible/inventory/group_vars/all/rsyslog.yml`) or only for a specific group
(in :file:`ansible/inventory/group_vars/logged/rsyslog.yml`), using:

.. code-block:: yaml

   rsyslog__forward: [ '*.* @logs.{{ ansible_domain }}' ]

This will forward logs on all hosts in the inventory over unencrypted UDP to
a specified host. Due to above "masking" of the variables on the host inventory
level, the log server should not create an infinite loop which forwards logs to
itself. The ``debops.rsyslog`` role does not handle such case automatically, so
you need to make sure this doesn't happen by accident.

The role by default supports more advanced setups like forwarding logs over TCP
using encrypted TLS connections, but these require more extensive configuration
from different Ansible roles. You should read the rest of the
``debops.rsyslog`` documentation to see how you can enable these features.

Example inventory
-----------------

To enable the ``debops.rsyslog`` role on a given host or group of hosts, you
need to add that host to the ``[debops_service_rsyslog]`` Ansible inventory
group:

.. code-block:: none

   [debops_service_rsyslog]
   hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.rsyslog`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rsyslog.yml
   :language: yaml
