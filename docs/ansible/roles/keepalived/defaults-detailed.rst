.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.keepalived`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _keepalived__ref_configuration:

keepalived__configuration
-------------------------

The ``keepalived__*_configuration`` variables define the contents of the
:file:`/etc/keepalived/keepalived.conf` configuration file. The syntax is
fairly simple and consists of blocks of the :man:`keepalived.conf(5)`
configuration data which can be enabled or disabled conditionally and allow use
of Jinja expressions to generate the desired configuration.

Examples
~~~~~~~~

.. _keepalived__example_floating_ip:

Floating IP address using :command:`keepalived`
'''''''''''''''''''''''''''''''''''''''''''''''

Create a floating IP address configuration distributed among a number of nodes
in a specific Ansible inventory group. Each node has a decreasing priority,
first node will be elected MASTER by default.

.. code-block:: none

   # ansible/inventory/cluster

   [debops_all_hosts]
   node1   ansible_host=node1.example.org
   node2   ansible_host=node2.example.org
   node3   ansible_host=node3.example.org

   [floating_ip_cluster]
   node1
   node2
   node3

   [debops_service_keepalived:children]
   floating_ip_cluster

.. code-block:: yaml

   ---
   # ansible/inventory/group_vars/floating_ip_cluster/keepalived.yml

   # Allow communication between keepalived nodes
   keepalived__group_allow: [ '192.0.2.0/24' ]

   # Name of the cluster Ansible inventory group
   keepalived__host_group: 'floating_ip_cluster'

   # keepalived configuration for all nodes
   keepalived__group_configuration:

     - name: 'vrrp_instance_1'
       raw: |
         vrrp_instance VI_1 {
             state {{ 'MASTER' if (keepalived__host_index | int == 0) else 'BACKUP' }}
             priority {{ (100 - (keepalived__host_index | int * 10)) }}
             interface eth0
             virtual_router_id 51
             advert_int 1
             authentication {
                 auth_type PASS
                 auth_pass 12345678
             }
             virtual_ipaddress {
                 192.0.2.10/24
             }
         }
       state: 'present'

You can find more configuration examples (notably, ``global_defs`` options) in
the :envvar:`keepalived__default_configuration` variable definition.

Syntax
~~~~~~

The ``keepalived__*_configuration`` variables are defined using a list of YAML
dictionaries. Each dictionary defines a configuration section using specific
parameters parsed via the :ref:`universal_configuration` filters:

``name``
  Required. Name of a given configuration entry, not used otherwise.
  Configuration entries with the same name are merged together during execution
  and can affect each other.

``raw``
  Required. YAML text block with :man:`keepalived.conf(5)` configuration
  options, added as-is in the generated configuration file. You can use Jinja
  expressions to create more dynamic configuration.

  The ``raw`` parameters in merged configuration entries override each other in
  order of appearance.

``comment``
  Optional. String or YAML text block with comments about a given configuration
  section, included in the generated configuration file.

``state``
  Optional. If not specified or ``present``, a given configuration section will
  be included in the generated configuration file. If ``absent``, a given
  configuration section will not be included in the generated configuration
  file. If ``ignore``, the configuration entry will not be evaluated during
  role execution.


.. _keepalived__ref_scripts:

keepalived__scripts
-------------------

Functionality of the :command:`keepalived` service can be extended via scripts
executed at certain events (see :man:`keepalived.conf` manual for more
details). The :ref:`debops.keepalived` provides a set of variables which can
be used to add or modify scripts (or other files, for example private keys or
certificates) stored in the :file:`/etc/keepalived/` directory. These files can
then be references in the :file:`/etc/keepalived/keepalived.conf` configuration
file to perform various functions.

Examples
~~~~~~~~

Use a script to start or stop services as needed on :command:`keepalived`
cluster state changes:

.. code-block:: yaml

   keepalived__configuration:

     - name: 'vrrp_vi_1'
       raw: |
         vrrp_instance vi_1 {
             notify /etc/keepalived/vi_1_notify.sh
         }

   keepalived__scripts:

    - name: 'vi_1_notify.sh'
      content: |
        #!/bin/bash

        TYPE=$1   # GROUP / INSTANCE
        NAME=$2   # name of group or instance
        STATE=$3  # MASTER / BACKUP / FAULT

        case $STATE in
                "MASTER") systemctl start nginx.service
                          exit 0
                          ;;
                "BACKUP") systemctl stop nginx.service
                          exit 0
                          ;;
                "FAULT")  systemctl stop nginx.service
                          exit 0
                          ;;
                *)        printf "unknown state\n"
                          exit 1
                          ;;
        esac
      state: 'present'


Syntax
~~~~~~

The ``keepalived__*_scripts`` variables define additional files that should be
included in the :file:`/etc/keepalived/` directory through a list of YAML
dictionaries with specific parameters:

``name`` or ``dest``
  Required. The name of the script or a file stored in the
  :file:`/etc/keepalived/` directory. The role does not create any required
  subdirectories automatically; it's best to keep all files and scripts
  confined in one directory.

``src``
  Path of the file located on Ansible Controller which should be copied to the
  remote host under a specified filename. This parameter shouldn't be used with
  the ``content`` parameter in the same file definition.

``content``
  YAML text block with the contents of the generated file. This parameter
  shouldn't be used with the ``src`` parameter in the same file definition.

``owner``
  Optional. Specify the UNIX account which should be the owner of the script or
  file managed by the role. If not specified, ``root`` is used by default.

``group``
  Optional. Specify the UNIX group which should be the main group of the script
  or file managed by the role. If not specified, ``root`` is used by default.

``mode``
  Optional. Specify the UNIX permissions mode for the generated file. If not
  specified, the role will use the ``0755`` mode by default, meant for
  executable scripts.

``state``
  Optional. If not specified or ``present``, a given file is copied or
  generated to the remote host. If ``absent``, a given file will be removed
  from the remote host.
