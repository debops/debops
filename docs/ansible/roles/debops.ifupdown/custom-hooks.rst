.. _ifupdown__ref_custom_hooks:

Custom :program:`ifupdown` hooks
================================

The ``debops.ifupdown`` Ansible role can configure custom :program:`ifupdown`
hooks in other software to configure services related to network interfaces.
The list of hooks can be found in the :envvar:`ifupdown__custom_hooks`
variable, which is a list of YAML dictionaries with specific parameters:

``name``
  Required. Name of the hook, used as an identifier.

``hook``
  Optional. Path of a Jinja2 template included with the :ref:`debops.ifupdown`
  role relative to the :file:`templates/` directory, which will be used to
  generate the hook script. The hook script will be placed at the same path on
  the target host.

``src``
  Optional. Override the path of the Jinja2 template (the ``.j2`` extension
  needs to be specified).

``dest``
  Optional. Override the path of the generated hook on the remote host (path
  needs to start with ``/``).

``mode``
  Optional. Set the file mode to use, by default ``0755``.

``state``
  Optional. If not specified or ``present``, the hook will be generated. If
  ``absent``, the hook will be removed.


.. _ifupdown__ref_custom_hooks_filter_dhcp_options:

The :program:`filter-dhcp-options` hook
---------------------------------------

This hook is a Bourne shell (:command:`/bin/sh`) script that is sourced by the
:man:`dhclient-script(8)` command executed by the :program:`dhclient` program
during interface configuration via DHCP. The hook allows to filter and ignore
received DHCP options per network interface, which can be useful on systems
connected to multiple networks with each one providing DHCP services. A list of
DHCP options can be found in the :man:`dhcp-options(5)` manual page.

By default the hook does not filter any DHCP options. To configure it, add the
``dhcp_ignore`` parameter in the :ref:`ifupdown__ref_interfaces` interface
configuration. The parameter is a string or list of variables used by the
:program:`dhclient-script` command to represent DHCP options.

Examples
~~~~~~~~

Consider configuration of a host connected to two networks, ``br0`` (internal
network) and ``br1`` (external network via a VLAN). By default the Debian
Installer sets up only the internal network connection which is used for host
configuration and management. The external connection is configured later, via
a VLAN which cannot be automatically configured by the Debian Installer. Both
networks are maintained using DHCP servers, each providing a default route
through its network.

After the host is configured, you want to switch the default route from the
internal network to the external network to allow public access to the services
provided by this host. To do that, the default route from the internal DHCP
server needs to be ignored, in which case the external network will take
precedence.

Additionally, the external DHCP server provides information about nameservers
that don't know about the internal network. You want to ignore the external
nameservers and use the ones provided by the internal network to resolve
queries, which lets you access other internal hosts via their hostnames.

.. code-block:: yaml

   ifupdown__host_interfaces:

     - iface: 'br0'
       comment: 'Internal network'
       type:  'bridge'
       inet:  'dhcp'
       inet6: 'auto'
       bridge_ports: 'eth0'
       dhcp_ignore: 'new_routers'

     - iface: 'br1'
       comment: 'External network'
       type:  'bridge'
       inet:  'dhcp'
       inet6: 'auto'
       bridge_ports: 'eth1'
       dhcp_ignore: 'new_domain_name_servers'

Just after installation the host will have only the internal network connection
set up, used for configuration. When Ansible applies the :ref:`debops.ifupdown`
configuration on the host, the default route to the external network will
replace the default route to the internal network, however existing internal
connections will work as usual. Any existing connections to the external
network via internal router might be interrupted before the new route takes
over.

The network configuration should be preserved across reboots - even though both
of the DHCP servers send relevant configuration for default routes and
nameservers, the DHCP options are filtered on the client side.
