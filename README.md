## debops.openvz
[![Platforms](http://img.shields.io/badge/platforms-debian-lightgrey.svg)](#)


`debops.openvz` role enables [OpenVZ](http://openvz.org/) container support
on Debian Wheezy hosts. This role has not been tested on Debian Jessie or
Ubuntu systems, and correct support for OpenVZ on these systems is at the
moment unlikely. Main reason for this role is to help ease transition from
older systems based on Debian Squeeze with OpenVZ into newer systems based
on Debian Wheezy/Jessie and LXC.

### Role dependencies

- debops.ferm


### Installation

To install `debops.openvz` using Ansible Galaxy, run:

    ansible-galaxy install debops.openvz


### Role variables

List of default variables available in the inventory:

    ---
    
    # ---- OpenVZ Cluster - global options ----
    
    # List of hosts in OpenVZ "cluster". These hosts will exchange SSH public keys
    # from their root accounts between them and record their SSH fingerprints for
    # easier container migration using vzmigrate.
    # By default it's all hosts in 'debops_openvz' group. You can change that by
    # defining a list of hosts using their inventory_hostname variable
    openvz_cluster: '{{ groups.debops_openvz }}'
    
    # Where OpenVZ containers are being stored? This preferably should be
    # a separate partition
    openvz_container_storage: '/var/lib/vz'
    
    # Default filesystem layout for new OpenVZ containers (simfs, ploop)
    openvz_storage_layout: 'ploop'
    
    
    # ---- Configuration file for new OpenVZ containers ----
    
    # Default configuration file for new OpenVZ containers
    openvz_configfile: 'vswap-debops'
    
    # How many containers do you plan to setup on an OpenVZ HN?
    openvz_configfile_container_count: '5'
    
    # Disk space soft limit multiplier
    openvz_configfile_diskspace_limit_multiplier: '0.7'
    
    # Disk inodes soft limit multiplier
    openvz_configfile_diskinodes_limit_multiplier: '0.9'
    
    # VSwap multiplier
    openvz_configfile_vswap_multiplier: '0.2'
    
    # How much RAM to reserve for the operating system?
    openvz_configfile_memory_padding: '256'
    
    # Quota time limit in seconds
    openvz_configfile_quotatime: '0'
    
    # Default cpuunits for new container
    openvz_configfile_cpuunits: '1000'
    
    # Default netfilter state for new containers
    # Choices: disabled, stateless, stateful, full
    openvz_configfile_netfilter: 'stateful'
    
    
    # ---- OpenVZ container template ----
    
    # Default container template
    openvz_template: 'debian-7.0-x86_64-minimal'
    
    # Should OpenVZ automatically update template images?
    openvz_template_update: 'yes'
    
    # Should OpenVZ check gnupg signature of a template image?
    openvz_template_signature: 'yes'
    
    # Where to look for online for OpenVZ templates
    openvz_template_prefix: 'http://download.openvz.org/template/precreated'
    
    # List of directories with "repositories" of templates on template server
    openvz_template_repos:
      - '{{ openvz_template_prefix }}'
      - '{{ openvz_template_prefix }}/contrib'
    
    
    # ---- OpenVZ kernel ----
    
    # Name of a kernel package (or metapackage) installed by openvz role
    openvz_kernel: 'linux-image-openvz-amd64'
    
    # Default GRUB menu entry to boot (counting from 0). When OpenVZ-enabled kernel
    # is installed, it will be placed just after the official Debian kernel. Recovery
    # option in GRUB should be disabled, which is the default when you use DebOps
    # Debian Preseed setup
    openvz_grub_default: '1'
    
    # Where to send mail reminders and alerts from openvz role
    openvz_mail_to: [ 'root@{{ ansible_domain }}' ]
    
    # List of IPv4 iptables kernel modules to be enabled in containers by default
    openvz_iptables: [ 'ipt_REJECT', 'ipt_tos', 'ipt_TOS', 'ipt_LOG', 'ip_conntrack',
                       'ipt_limit', 'ipt_multiport', 'iptable_filter', 'iptable_mangle',
                       'ipt_TCPMSS', 'ipt_tcpmss', 'ipt_ttl', 'ipt_length', 'ipt_state',
                       'iptable_nat', 'ip_nat_ftp' ]



List of internal variables used by the role:

    openvz_configfile_calculated_diskspace
    openvz_configfile_calculated_total_memory
    openvz_configfile_calculated_diskinodes_limit
    openvz_configfile_calculated_diskinodes
    openvz_configfile_calculated_ram
    openvz_configfile_calculated_diskspace_limit
    openvz_root_ssh_key
    openvz_configfile_calculated_vswap


### Detailed usage guide

This role is meant to create and manage OpenVZ Hardware Nodes, not OpenVZ
containers themselves.

`debops.openvz` role uses [Linux kernel from
openvz.org](https://openvz.org/Installation_on_Debian) (2.6.32), which is
older than the default kernel in Wheezy (3.2.0). Because of that various
technologies from Wheezy (KVM, LXC for example) might be incompatible with
older kernel. Thus, this role should not be mixed on one host with those
technologies.

Because of the kernel downgrade, a reboot of the host will be required, but
`debops.openvz` will not reboot managed hosts automatically. Instead, an
email will be sent to root account in case a kernel downgrade or update is
performed, to notify the administrator about required reboot. This lets the
administrator schedule reboots at their convenience. Make sure that your
Hardware Nodes have correct mail setup to forward mails to administrators,
for example with `debops.postfix` role.

You can specify a group of hosts (by default role looks for
`[debops_openvz]` group), in which case they will be treated as a cluster
of OpenVZ Hardware Nodes. Each HN will create an SSH keypair on its `root`
account, and these keys will be automatically distributed among nodes in
the cluster, and the host SSH fingerprints will be registered on each node
`~/.ssh/known_hosts` file. This allows you to easily migrate containers
between Hardware Nodes with `vzmigrate` command.


### Authors and license

`debops.openvz` role was written by:

- Maciej Delmanowski - [e-mail](mailto:drybjed@gmail.com) | [Twitter](https://twitter.com/drybjed) | [GitHub](https://github.com/drybjed)


License: [GNU General Public License v3](https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3))


***

This role is part of the [DebOps](http://debops.org/) project. README generated by [ansigenome](https://github.com/nickjj/ansigenome/).

