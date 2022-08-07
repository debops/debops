.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind__ref_default_setup:

Default setup
-------------

If you don't specify any configuration values, the role will setup BIND
as a caching nameserver which is neither an authoritative, nor a secondary
server for any domains/zones.

In addition, `DNSSEC`__ validation is enabled (i.e. DNSSEC is enabled when BIND
acts as a resolver). The configuration is also prepared with policies which
allow BIND to perform largely automatic :ref:`DNSSEC signing
<bind__ref_dnssec>` of zones, on an opt-in basis.

.. __: https://en.wikipedia.org/wiki/Domain_Name_System_Security_Extensions

When a valid :ref:`Public Key Infrastructure <debops.pki>` is detected,
and the installed version of BIND supports it, support for
:ref:`bind__ref_dot_doh` is also enabled, either in a standalone fashion or,
if the role is detected, using :ref:`debops.nginx` as a reverse proxy.

Initial zones can be created using the Ansible inventory (see
:ref:`bind__ref_zones`) and later updated dynamically using e.g.
:command:`nsupdate`.

The role also supports the automatic generation of keys, which can be used
to authenticate e.g. update requests or to provision other roles with keys
to be used for automated DNS updates. These keys are, by default, also
stored on the Ansible controller (in the directory tree maintained by
the :ref:`debops.secret` role) for further use.


.. _bind__ref_example_inventory:

Example inventory
-----------------

To install and configure BIND on a host, it needs to be present in the
``[debops_service_bind]`` Ansible inventory group. Additionally, if you
plan to run a web server on the same host at some point, it is a good idea
to define that in the inventory before you apply this role, as a later
installation may clash with features such as :ref:`bind__ref_dot_doh`.

.. code-block:: none

   [debops_all_hosts]
   dns

   [debops_service_nginx]
   dns

   [debops_service_bind]
   dns


.. _bind__ref_example_playbook:

Example playbook
----------------

The following playbook can be used with DebOps. If you are using these role
without DebOps you might need to adapt them to make them work in your setup.

.. literalinclude:: ../../../../ansible/playbooks/service/bind.yml
   :language: yaml
   :lines: 1,5-

This playbook is also shipped with DebOps as
:file:`ansible/playbooks/service/bind.yml`.


.. _bind__ref_ansible_tags:

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::bind``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::bind:backup``
  Run tasks related to the backup script.

``role::bind:config``
  Run tasks related to the BIND configuration.

``role::bind:dnssec``
  Run tasks related to DNSSEC.

``role::bind:keys``
  Run tasks related to key generation/download/etc.

``role::bind:packages``
  Run tasks related to system package installation.

``role::bind:pki``
  Run tasks related to the PKI integration.
