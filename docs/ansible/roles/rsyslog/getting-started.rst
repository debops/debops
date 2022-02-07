.. Copyright (C) 2015-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Initial configuration
---------------------

The ``debops.rsyslog`` default configuration is designed to closely resemble
the Debian ``rsyslog`` package defaults. The same system logs will be
generated, although with slightly longer log rotation. If the operating system
is Debian, ``rsyslog`` will be run on a privileged ``root`` account; if the
system is Ubuntu, an unprivileged ``syslog`` account will be used by default.


Configuration filename extensions
---------------------------------

The configuration order is important, and to aid support of configuration from
other roles, the :file:`/etc/rsyslog.conf` configuration file includes other
configuration files with different filename extensions at certain points of the
configuration:

:file:`/etc/rsyslog.d/*.input`
  These files define configuration of the `rsyslog input modules`__ which can
  be used as data sources.

  .. __: https://www.rsyslog.com/doc/v8-stable/configuration/modules/idx_input.html

:file:`/etc/rsyslog.d/*.template`
  These configuration files can be used to create custom templates used by
  ``rsyslog`` in different parts of the configuration.

:file:`/etc/rsyslog.d/*.conf`
  These files are included by default. They are meant to be used for
  configuration of the local system logs, the extension is used to preserve
  compatibility with Debian package conventions.

:file:`/etc/rsyslog.d/*.output`
  These files define configuration of the `rsyslog output modules`__ which can
  be used as targets by various local and remote rulesets defined later on.

  .. __: https://www.rsyslog.com/doc/v8-stable/configuration/modules/idx_output.html

:file:`/etc/rsyslog.d/*.ruleset`
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

`Log forwarding`__ tells :command:`rsyslogd` server to send all, or select,
syslog messages to remote syslog server(s). The :ref:`debops.rsyslog` role is
tailored to perform log forwarding over TLS to a central syslog server using
:ref:`dns_configuration_srv` for the following service:

.. __: https://www.rsyslog.com/sending-messages-to-a-remote-syslog-server/

.. code-block:: none

   _syslog._tcp.{{ rsyslog__domain }} (default port 6514)

If:

- the resource records are found; *and*

- the host is not configured to receive logs via the
  :envvar:`rsyslog__remote_enabled` variable; *and*

- the :ref:`debops.pki` role has been configured on the host

Then the :ref:`debops.rsyslog` role will configure each target server to send
syslog messages over TLS. This configuration can be found and changed in the
:envvar:`rsyslog__default_forward` and the :envvar:`rsyslog__default_rules`
variables.


Quick start: receiving remote logs
----------------------------------

The role does not configure :command:`rsyslogd` service to receive log messages
from the network by default. To enable this, you can specify a list of allowed
IP addresses and/or CIDR subnets which are allowed to send syslog messages
using the :envvar:`rsyslog__allow`, :envvar:`rsyslog__group_allow` and/or
:envvar:`rsyslog__host_allow` variables. Defining these in the inventory will
tell the role to configure :command:`rsyslog` to accept remote logs and store
them in subdirectories under the :file:`/var/log/remote/` directory. The
:ref:`debops.ferm` and the :ref:`debops.logrotate` roles will be used to
configure the IPTables firewall and log rotation respectively.

This behaviour is controlled by the :envvar:`rsyslog__remote_enabled` variable.


Example inventory
-----------------

The :ref:`debops.rsyslog` role is included by default in the DebOps
:file:`common.yml` playbook and does not need to be specifically enabled.

To enable the ``debops.rsyslog`` role on a given host or group of hosts not
managed by DebOps, you need to add that host to the
``[debops_service_rsyslog]`` Ansible inventory group:

.. code-block:: none

   [debops_service_rsyslog]
   hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.rsyslog`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rsyslog.yml
   :language: yaml
   :lines: 1,5-
