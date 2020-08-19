Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Which version to use
--------------------

The current version of `dropbear <https://packages.debian.org/search?keywords=dropbear>`__ provided in Debian jessie is a bit
old and does not provide SOTA_ cryptography.
The role already supports the updated dropbear version from Debian stretch which is now available as
`dropbear-initramfs <https://packages.debian.org/search?keywords=dropbear-initramfs>`_.
The proper way to install it on Debian jessie is to use debops.reprepro_.

It has also been tested to install the version from stretch on jessie. Note
that this is discouraged by Debian and DebOps but you might decide to make an
exception in this case when you know what you are doing.

If you do, all you have to do is to enable the stretch repositories and use APT
pinning to ensure that no unwanted packages are pulled from stretch. And tell
``debops-contrib.dropbear_initramfs`` that you want the newer version.
If you are using DebOps, you can set the following in your inventory:

.. code-block:: yaml

   ## Load APT pinning presets.
   apt_preferences__group_list:
     - '{{ apt_preferences__preset_list | list }}'

   apt__group_sources:
     - comment: 'Enable Debian stretch repository'
       uri: '{{ ansible_local.apt.default_sources_map.Debian[0]
                if (ansible_local|d() and ansible_local.apt|d() and
                    ansible_local.apt.default_sources_map|d() and
                    ansible_local.apt.default_sources_map.Debian|d() and
                    ansible_local.apt.default_sources_map.Debian[0]|d())
                else "http://deb.debian.org/debian" }}'
       suites:
         - 'stretch'
       component:
         - 'main'

   dropbear_initramfs__base_packages:
     - 'dropbear-initramfs'

Example inventory
-----------------

To setup the dropbear ssh server in initramfs of a given host or a set of hosts, they need to
be added to the ``[debops_service_dropbear_initramfs]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_dropbear_initramfs]
   hostname

Example playbook
----------------

Here's an example playbook that uses the ``debops-contrib.dropbear_initramfs`` role:

.. literalinclude:: playbooks/dropbear_initramfs.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/dropbear_initramfs.yml` from which you can symlink it
to your playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::dropbear_initramfs``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::dropbear_initramfs:pkgs``
  Tasks related to system package management like installing or
  removing packages.
