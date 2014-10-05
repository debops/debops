|DebOps| ifupdown
#################

.. |DebOps| image:: http://debops.org/images/debops-small.png
   :target: http://debops.org

|Travis CI| |test-suite| |Ansible Galaxy|

.. |Travis CI| image:: http://img.shields.io/travis/debops/ansible-ifupdown.svg?style=flat
   :target: http://travis-ci.org/debops/ansible-ifupdown

.. |test-suite| image:: http://img.shields.io/badge/test--suite-ansible--ifupdown-blue.svg?style=flat
   :target: https://github.com/debops/test-suite/tree/master/ansible-ifupdown/

.. |Ansible Galaxy| image:: http://img.shields.io/badge/galaxy-debops.ifupdown-660198.svg?style=flat
   :target: https://galaxy.ansible.com/list#/roles/1570



This role can be used to manage network interface configuration on Debian
and derivative operating systems. It manages configuration in
``/etc/network/interfaces`` directory and can be used to create different
interface layouts across the cluster.

``debops.ifupdown`` role tries to recognize several environments (LXC
container, OpenVZ container, system with installed NetworkManager) and can
automatically select one of the suggested configurations. For most
scenarios, ``debops.ifupdown`` will try to configure up to two network
interfaces (non-existent interfaces are gracefully skipped) with network
bridges attached to them, which allows to easily connect virtual machines
or containers to the public or private network.

In case an advanced configuration is required (more than two network
interfaces, bonding, modem connections, NAT, etc.), you can easily override
automatically selected configuration using Ansible inventory. This role can
also be used as a dependency of another role which allows for example to
easily manage NAT networks using ``debops.nat`` role.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v1.7.0``. To install it, run:

::

    ansible-galaxy install debops.ifupdown

Are you using this as a standalone role without DebOps?
=======================================================

You may need to include missing roles from the `DebOps common playbook`_
into your playbook.

`Try DebOps now`_ for a complete solution to run your Debian-based infrastructure.

.. _DebOps common playbook: https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml
.. _Try DebOps now: https://github.com/debops/debops/




Role variables
~~~~~~~~~~~~~~

List of default variables available in the inventory:

::

    ---
    
    # Should Ansible manage /etc/network/interfaces? Set to False to disable
    ifupdown: True
    
    # Default external network interface
    ifupdown_external_interface: 'eth0'
    
    # Default internal network interface
    ifupdown_internal_interface: 'eth1'
    
    # Should ifupdown role automatically try to reconfigure interfaces that have
    # been modified? Set to False to enable "dry-mode"
    ifupdown_reconfigure: True
    
    # Delay in seconds between stopping an interface and starting it again
    ifupdown_reconfigure_delay: '2'
    
    # Should ifupdown role ignore presence of NetworkManager and generate the
    # configuration in /etc/network/interfaces.d/?
    ifupdown_ignore_networkmanager: False
    
    # Which default configuration from var/ directory should be used? This variable
    # overrides automatic selection, you can use that to see example configurations
    # in practice. Specify a filename without '.yml' extension
    ifupdown_default_config: ""
    
    # List of network interfaces. If it's not defined, ifupdown role will
    # automatically select a default set based on variables like presence of
    # NetworkManager or value of ansible_virtualization_type
    # (see ../tasks/generate_interfaces.yml). Default sets are defined in ../vars/*
    # files.
    # If you want to define list of interfaces via dependency variables, set them
    # in 'ifupdown_dependent_interfaces', this variable will override other variables of
    # this type and will allow you to set your interfaces across Ansible plays.
    # Refer to interfaces(5) and https://wiki.debian.org/NetworkConfiguration to
    # see possible configuration options.
    ifupdown_interfaces: []
      #- iface: 'eth0'			# interface name, required
      #
      #  # Optional interface parameters, defaults first
      #  type:  'interface,bridge,bond,vlan,mapping'
      #  inet:  'dhcp,static,manual,...'	# mode of operation for IPv4
      #  inet6: 'dhcp,static,manual,...'	# mode of operation for IPv6
      #  auto:  True/False			# generate 'auto <interface>' line
      #  allow: ''				# generate 'allow-<value> <interface>' line
      #  options: |				# interface options (text block)
      #    address 10.0.0.1
      #    netmask 255.255.255.0
      #    # ...
      #  aliases:				# list of additional IP addresses for interface
      #    - address: '192.168.0.2'
      #      netmask: '255.255.255.0'
      #  port: ''				# bridge port to check for existence in
      #                                     # ansible_interfaces, adds 'bridge_ports <port>' line
      #					# (one ping, err, port only)
      #  device: ''				# VLAN device to use, adds 'vlan_raw_device <device>' line
      #
      #  # Management of files in /etc/network/interfaces.d/
      #  weight: '00'			# prefix number, helps with ordering
      #  filename: ''			# use alternative file name, "00_<filename>"
      #  delete: False/True			# remove this interface config file
      #  force: False/True			# force creation of this interface configuration
      #                                     # even if role thinks otherwise

List of internal variables used by the role:

::

    ifupdown_networkmanager
    ifupdown_interfaces


Authors and license
~~~~~~~~~~~~~~~~~~~

``ifupdown`` role was written by:

- Maciej Delmanowski | `e-mail <mailto:drybjed@gmail.com>`_ | `Twitter <https://twitter.com/drybjed>`_ | `GitHub <https://github.com/drybjed>`_

License: `GPLv3 <https://tldrlegal.com/license/gnu-general-public-license-v3-%28gpl-3%29>`_

****

This role is part of the `DebOps`_ project. README generated by `ansigenome`_.

.. _DebOps: http://debops.org/
.. _Ansigenome: https://github.com/nickjj/ansigenome/
