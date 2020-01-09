.. _ferm__ref_firewall_rules:

Firewall Rule Definitions
=========================

Firewall configuration in ``debops.ferm`` is done through a flexible
definition of rules. There are a number of variables which are used to
reference a set of default rules and can be extended by user defined
rules. Here a description of the involved configurations should be given
so that everyone can customize the ruleset according to individual
requirements.

.. contents::
   :local:
   :depth: 2

.. _ferm__ref_default_rules:

Default rules
-------------

By default ``debops.ferm`` configures a number of rules as soon as a
host is part of the ``[debops_all_hosts]`` Ansible host group. The rules
created by default are defined in :file:`defaults/main.yml` and activated by
being listed in :envvar:`ferm__default_rules`. They consist of basic rules for
setting the :command:`iptables` default policies, restricting extensive connection
attempts, logging and more.

In case a firewall is not required or preferred this behaviour can be
disabled by setting :envvar:`ferm__enabled` to ``False`` in the inventory.


.. _ferm__ref_custom_rules:

Custom rules
------------

A custom rule can be enabled by adding a rule definition to one of the
predefined rule lists (:envvar:`ferm__rules`, :envvar:`ferm__group_rules`,
:envvar:`ferm__host_rules` or :envvar:`ferm__dependent_rules`) in the Ansible
inventory. Each rule has to be defined as a YAML dict using some of
the following keys:

``domain``
  Optional. :command:`iptables` domain used for the firewall rule. Possible values:
  :command:`ip`, ``ip6``. Defaults to :envvar:`ferm__domains`.

``table``
  Optional. :command:`iptables` table to which the rule is added or from which it
  is removed. Defaults to ``filter``.

``chain``
  Optional. :command:`iptables` chain to which the rule is added or from which it
  is removed. Defaults to ``INPUT``.

``by_role``
  Optional. Name of the Ansible role in the format ``ROLE_OWNER.ROLE_NAME``
  which is responsable for the rule. This will be included as a comment in the
  generated rule file.

Depending on the chosen type, many additional variables are supported.
Please check the individual rule type description below.


.. _ferm__ref_rule_types:

Rule types
----------

There exist a number of predefined rule types for generating firewall rules
through :command:`ferm`. Following a list of the available rule types which can
be used to create custom rules.


.. _ferm__ref_type_accept:

The 'accept' type
~~~~~~~~~~~~~~~~~

This rule type can be used to create rules that match interfaces, ports, remote
IP addresses/subnets and can accept the packets, reject, or redirect to
a different chain. The following type-specific YAML keys are supported:

``accept_any``
  Optional. Match all source addresses by default. Possible values: ``True``
  or ``False``. Defaults to ``True``. If this option is set to ``False`` and
  ``item.target`` is set to ``REJECT`` all traffic is blocked by default.
  As soon as ``item.saddr`` is not empty, this configuration doesn't matter
  anymore.

``daddr``
  Optional. List of destination IP addresses or networks to which the
  rule is applied.

``dport``
  Optional. List of destination ports to which the rule is applied.

``include``
  Optional. Custom :command:`ferm` configuration file to include.
  See `ferm include`_ for more details.

``interface``
  Optional. List of network interfaces for incoming packets to which the
  rule is applied.

``interface_present``
  Optional. Same as ``item.interface`` but first check if specified network
  interfaces exists before adding the firewall rules.

``multiport``
  Optional. Use ``iptables multiport`` extension. Possible values: ``True``
  or ``False``. Defaults to ``False``.

``outerface``
  Optional. List of network interfaces for outgoing packets to which the
  rule is applied.

``outerface_present``
  Optional. Same as ``item.outerface`` but first check if specified network
  interface exists before adding the firewall rule.

``protocol``
  Optional. Network protocol to which the rule is applied.

``protocol_syn``
  Optional. Match TCP packet with only the SYN flag set. Possible values
  ``True`` or ``False``. If set to ``False`` it will match all other packets
  except the ones with only the SYN flag set. Defaults to unset.

``realgoto``
  Optional. After packet match jump to custom chain. See `ferm realgoto`_ for
  more details.

``reject_with``
  Optional. Define reject message being sent when the rule ``item.target`` is
  set to ``REJECT``. Defaults to ``icmp-admin-prohibited``.

``saddr``
  Optional. List of source IP addresses or networks to which this rule is
  applied.

``sport``
  Optional. List of source ports to which the rule is applied.

``state``
  Optional. Connection state which should be matched. Possible values:
  ``INVALID``, ``ESTABLISHED``, ``NEW``, ``RELATED``, ``UNTRACKED`` or
  comma-separated combination thereof.

``subchain``
  Optional. Subchain name. If more than 3 addresses are listed in
  ``target.saddr`` move resulting :command:`iptables` rules into a separate subchain
  with the given name. See `ferm subchain`_ for more details.

``target``
  Optional. :command:`iptables` jump target. Possible values: ``ACCEPT``, ``DROP``,
  ``REJECT``, ``RETURN``, ``NOP`` or a custom target. Defaults to ``ACCEPT``.

.. _ferm include: http://ferm.foo-projects.org/download/2.1/ferm.html#includes
.. _ferm realgoto: http://ferm.foo-projects.org/download/2.1/ferm.html#realgoto_custom_chain_name
.. _ferm subchain: http://ferm.foo-projects.org/download/2.1/ferm.html#_subchain


.. _ferm__ref_type_ansible_controller:

The 'ansible_controller' type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to the ``accept`` type but defaults to the SSH target port and sets the
source address to the host running Ansible if not overwritten through the
``item.ansible_controllers`` key. The following type-specific YAML keys are
supported:

``ansible_controllers``
  Optional. List of source IP address which are added to ``item.saddr``.
  Overwrites auto-detection of the Ansible controller address.

``daddr``
  Optional. List of destination IP addresses or networks to which the rule
  is applied.

``dport``
  Optional. List of destination ports to which the rule is applied. Defaults
  to :command:`ssh`.

``include``
  Optional. Custom ferm configuration file to include. See `ferm include`_
  for more details.

``interface``
  Optional. List of network interfaces for incoming packets to which the
  rule is applied.

``multiport``
  Optional. Use `iptables multiport`_ extension. Possible values: ``True``
  or ``False``. Defaults to ``False``.

``outerface``
  Optional. List of network interfaces for outgoing packets to which the
  rule is applied.

``protocol``
  Optional. Network protocol to which the rule is applied. Defaults to ``tcp``.

``protocol_syn``
  Optional. Match TCP packet with only the SYN flag set. Possible values
  ``True`` or ``False``. If set to ``False`` it will match all other packets
  except the ones with only the SYN flag set. Defaults to unset.

``realgoto``
  Optional. After packet match jump to custom chain. See `ferm realgoto`_ for
  more details.

``reject_with``
  Optional. Define reject message being sent when the rule ``item.target`` is
  set to ``REJECT``. Defaults to ``icmp-admin-prohibited``.

``saddr``
  Optional. List of source IP addresses or networks to which this rule is
  applied.

``sport``
  Optional. List of source ports to which the rule is applied.

``state``
  Optional. Connection state which should be matched. Possible values:
  ``INVALID``, ``ESTABLISHED``, ``NEW``, ``RELATED``, ``UNTRACKED`` or
  comma-separated combination thereof.

``subchain``
  Optional. Subchain name. If more than 3 addresses are listed in
  ``target.saddr`` move resulting :command:`iptables` rules into a separate subchain
  with the given name. See `ferm subchain`_ for more details.

``target``
  Optional. :command:`iptables` jump target. Possible values: ``ACCEPT``, ``DROP``,
  ``REJECT``, ``RETURN``, ``NOP`` or a custom target. Defaults to ``ACCEPT``.

.. _iptables multiport: http://ipset.netfilter.org/iptables-extensions.man.html#lbBM


.. _ferm__ref_type_connection_tracking:

The 'connection_tracking' type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This type is used to enable connection tracking using the `iptables conntrack`_
or `iptables state`_ extension. The following type-specific YAML keys are
supported:

``tracking_active_target``
  Optional. :command:`iptables` jump target for valid connections. Defaults to
  ``ACCEPT``.

``tracking_invalid_target``
  Optional. :command:`iptables` jump target for invalid connections. Defaults to
  ``DROP``.

``tracking_module``
  Optional. :command:`iptables` module used for connection tracking. Possible values:
  ``state`` or ``conntrack``. Defaults to ``conntrack``.

``interface``
  Optional. List of network interfaces for incoming packets to which the rule
  is applied.

``outerface``
  Optional. List of network interfaces for outgoing packets to which the rule
  is applied.

``interface_not``
  Optional. List of network interfaces for incoming packets which are excluded
  from the rule.

``outerface_not``
  Optional. List of network interfaces for outgoing packets which are excluded
  from the rule.

.. _iptables conntrack: http://ipset.netfilter.org/iptables-extensions.man.html#lbAO
.. _iptables state: http://ipset.netfilter.org/iptables-extensions.man.html#lbCC


.. _ferm__ref_type_custom:

The 'custom' type
~~~~~~~~~~~~~~~~~

The type used to define custom :command:`ferm` rules. The following additional
YAML keys are supported:

``rules``
  ferm rule definition, required.

``by_role``
  Optional. Add comment to generated ferm rule definition file that rule is
  defined in the given Ansible role.

This template is used among others in a :ref:`debops.libvirtd` custom ferm rule.


.. _ferm__ref_type_default_policy:

The 'default_policy' type
~~~~~~~~~~~~~~~~~~~~~~~~~

This type is used to define :command:`iptables` default policies. The following
type-specific YAML keys are supported:

``policy``
  :command:`iptables` chain policy, required.


.. _ferm__ref_type_dmz:

The 'dmz' type
~~~~~~~~~~~~~~

This type can be used to enable connection forwarding to another host. If
``item.port`` is not specified, all traffic is forwarded. The following
type-specific YAML keys are supported:

``multiport``
  Optional. Use `iptables multiport`_ extension. Possible values: ``True``
  or ``False``. Defaults to ``False``.

``interface``
  Optional. List of public network interfaces which accept connections.
  At least one of ``interface`` or ``public_ip`` is required.

``public_ip``
  Optional. IPv4 address on the public network which accepts connections.
  At least one of ``interface`` or ``public_ip`` is required. Only 1 IP address
  should be used at a time.

``private_ip``
  IPv4 address of the host on the internal network, required. Only 1 IP address
  should be used at a time.

``protocol(s)``
  Optional. List of protocols to forward. Defaults to ``tcp``.

``port(s)``
  Optional. List of ports to forward.

``dport``
  Optional. Destination port to forward to. Only needs to be specified if
  internal destination port is different from the original destination port.

``snat_ip``
  Optional. IP address for source address translation. If set the source IP is
  rewritten to this address. This is typically the IP address of the firewall
  host on the internal network. This is useful if traffic from the ``private_ip``
  would otherwise not be routed back to the firewall host.


.. _ferm__ref_type_hashlimit:

The 'hashlimit' type
~~~~~~~~~~~~~~~~~~~~

This type is used to define rate limit rules using the `iptables hashlimit`_
extension. The following type-specific YAML keys are supported:

``daddr``
  Optional. List of destination IP addresses or networks to which the
  rule is applied.

``dport``
  Optional. List of destination ports to which the rule is applied.

``hashlimit_burst``
  Optional. Number of packets to match within the expiration time. Defaults
  to ``5``.

``hashlimit_expire``
  Optional. Expiration time of hash entries in seconds. Defaults to ``1.8``.

``hashlimit_target``
  Optional. Jump target used when packet matches the ``hashlimit`` rule which
  means that the rate limit is not reached yet. Defaults to ``RETURN``.

``hashlimit_mode``
  Optional. Options to take into consideration when associating packet
  streams. Possible values: ``srcip``, ``srcport``, ``dstip``, ``dstport``
  or a comma-separated list thereof. Defaults to ``srcip``.

``interface``
  Optional. List of network interfaces for incoming packets to which the
  rule is applied.

``interface_present``
  Optional. Same as ``item.interface`` but first check if specified network
  interfaces exists before adding the firewall rules.

``outerface``
  Optional. List of network interfaces for outgoing packets to which the
  rule is applied.

``outerface_present``
  Optional. Same as ``item.outerface`` but first check if specified network
  interface exists before adding the firewall rule.

``include``
  Optional. Custom ferm configuration file to include. See `ferm include`_ for
  more details.

``log``
  Optional. Write rate limit hits to syslog. Possible values: ``True`` and
  ``False``. Defaults to ``True``.

``protocol``
  Optional. Network protocol to which the rule is applied.

``protocol_syn``
  Optional. Match TCP packet with only the SYN flag set. Possible values
  ``True`` or ``False``. If set to ``False`` it will match all other packets
  except the ones with only the SYN flag set. Defaults to unset.

``reject_with``
  Optional. Define reject message being sent when the rule ``item.target`` is
  set to ``REJECT``. Defaults to ``icmp-admin-prohibited``.

``state``
  Optional. Connection state which should be matched. Possible values:
  ``INVALID``, ``ESTABLISHED``, ``NEW``, ``RELATED``, ``UNTRACKED`` or
  comma-separated combination thereof.

``subchain``
  Optional. Subchain name. Move resulting :command:`iptables` rules into a
  separate subchain with the given name. See `ferm subchain`_ for more
  details.

``target``
  Optional. :command:`iptables` jump target in case the rate limit is reached.
  Defaults to ``REJECT``.

.. _iptables hashlimit: http://ipset.netfilter.org/iptables-extensions.man.html#lbAY


.. _ferm__ref_type_include:

The 'include' type
~~~~~~~~~~~~~~~~~~

This type can be used to include custom :command:`ferm` configuration files.
The following type-specific YAML keys are supported:

``include``
  Optional. Custom ferm configuration file to include. See
  `ferm include`_ for more details.


.. _ferm__ref_type_log:

The 'log' type
~~~~~~~~~~~~~~

This type can be used to specify logging rules using the `iptables log`_
extension. The following type-specific YAML keys are supported:

``include``
  Optional. Custom :command:`ferm` configuration file to include. See
  `ferm include`_ for more details.

``log_burst``
  Optional. Burst limit of packets being logged. Defaults to
  :envvar:`ferm__log_burst`.

``log_ip_options``
  Optional. Log IP options of packet. Possible values: ``True`` or ``False``.
  Defaults to ``True``.

``log_level``
  Optional. Log level for firewall messages. Possible values are: ``emerg``,
  ``alert``, ``crit``, ``error``, ``warning``, ``notice``, ``info`` or
  ``debug``. Defaults to ``warning``.

``log_limit``
  Optional. Rate limit of packets being logged. Defaults to
  :envvar:`ferm__log_limit`.

``log_prefix``
  Optional. Prefix (up to 29 characters) for firewall log messages. Defaults
  to :command:`iptables-log:`

``log_target``
  Optional. Select how :command:`iptables` performs logging. Possible values:
  ``LOG``, ``ULOG``, ``NFLOG``. Defaults to ``LOG``.

``log_tcp_options``
  Optional. Log TCP options of packet. Possible values: ``True`` or ``False``.
  Defaults to ``False``.

``log_tcp_sequence``
  Optional. Log TCP sequence of packet. Possible values: ``True`` or
  ``False``. Defaults to ``False``.

``realgoto``
  Optional. After packet match jump to custom chain. See `ferm realgoto`_ for
  more details.

``reject_with``
  Optional. Define reject message being sent when the rule ``item.target`` is
  set to ``REJECT``. Defaults to ``icmp-admin-prohibited``.

``target``
  Optional. :command:`iptables` jump target for logged packets.

.. _iptables log: http://ipset.netfilter.org/iptables-extensions.man.html#lbDD


.. _ferm__ref_type_recent:

The 'recent' type
~~~~~~~~~~~~~~~~~

This type can be used to track connections and respond accordingly by using the
`iptables recent`_ extension. The following type-specific YAML keys are
supported:

``dport``
  Optional. List of destination ports to which the rule is applied.

``include``
  Optional. Custom ferm configuration file to include. See
  `ferm include`_ for more details.

``multiport``
  Optional. Use `iptables multiport`_ extension. Possible values: ``True``
  or ``False``. Defaults to ``False``.

``protocol``
  Optional. Network protocol to which the rule is applied.

``protocol_syn``
  Optional. Match TCP packet with only the SYN flag set. Possible values
  ``True`` or ``False``. If set to ``False`` it will match all other packets
  except the ones with only the SYN flag set. Defaults to unset.

``recent_hitcount``
  Optional. Must be used in combination with ``item.recent_update``. Match
  if address is in the list and at least the given number of packets were
  received so far.

``recent_log``
  Optional. Log packets matching the rule. Possible values: ``True`` or
  ``False``. Defaults to :envvar:`ferm__log`. If this is set to ``True``
  :envvar:`ferm__log` must be enabled too for the packet to be logged.

``recent_name``
  Optional. Name of the list. Defaults to ``DEFAULT``.

``recent_remove``
  Optional. Remove address from the list. Possible values: ``True`` or
  ``False``. Defaults to ``False``. Mutually exclusive with
  ``item.recent_update``.

``recent_seconds``
  Optional. Must be used in combination with ``item.recent_update``. Match
  if address is in the list and was last seen within the given number of
  seconds.

``recent_set_name``
  Optional. Add the source address of a matching packet to the given list. This
  must correspond with ``item.recent_name`` of a second rule which would
  potentially act on the packet, e. g. reject it.

``recent_target``
  Optional. :command:`iptables` jump target when packet has hit the recent list.
  Possible values: ``ACCEPT``, ``DROP``, ``REJECT``, ``RETURN``, ``NOP`` or
  a custom target. Defaults to ``NOP``.

``recent_update``
  Optional. Update "last-seen" timestamp.  Possible values: ``True`` or
  ``False``. Defaults to ``False``. Mutually exclusive with
  ``item.recent_remove``.

``reject_with``
  Optional. Define reject message being sent when the rule ``item.target`` is
  set to ``REJECT``. Defaults to ``icmp-admin-prohibited``.

``state``
  Optional. Connection state which should be matched. Possible values:
  ``INVALID``, ``ESTABLISHED``, ``NEW``, ``RELATED``, ``UNTRACKED`` or
  comma-separated combination thereof.

``subchain``
  Optional. Subchain name. Move resulting :command:`iptables` rules into a
  separate subchain with the name given. See `ferm subchain`_ for more
  details.

When using the ``recent`` type make sure to always define two
rules:

* One for matching the packet against the address list using the
  ``item.recent_update`` feature. If this filter matches you likely want
  to set the ``item.recent_target`` to ``DROP`` or ``REJECT``.

* To clear the source address from the list again in case the connection
  restrictions are not met, add a second role using ``item.recent_remove``.

.. _iptables recent: http://ipset.netfilter.org/iptables-extensions.man.html#lbBW


.. _ferm__ref_type_reject:

The 'reject' type
~~~~~~~~~~~~~~~~~

This type is used to reject all traffic. It can be added for example as a final
rule in a custom chain.


.. _ferm__ref_legacy_rules:

Legacy rules
------------

Legacy rules are the (old) deprecated way to configure firewall rules
using a simpler less flexible syntax than described above. As support
for these is likely going to be removed in the future, they shouldn't be
used anymore.

Support for legacy rules is still enabled by default. However, they are
stored in a separate :command:`iptables` INPUT chain called
``debops-legacy-input-rules``. In case you haven't defined any legacy
rules and none of the DebOps roles you are using are still depending
on it, disable support completely by setting :envvar:`ferm__include_legacy`
to ``False`` which will avoid the additional chain from being created.

If you're not sure if you still have legacy rules defined, look for
variable names with only on '_' after the :program:`ferm` prefix (e. g.
:envvar:`ferm_input_list` and :envvar:`ferm_input_dependent_list`).
