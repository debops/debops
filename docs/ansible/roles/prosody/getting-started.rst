.. Copyright (C) 2018 Norbert Summer <git@o-g.at>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Default configuration
---------------------

The configuration is split into 3 basic parameters,
this is because of limitation of YAML and easier representation.

- prosody__*_config_global
- prosody__*_config_components
- prosody__*_config_virtual_hosts

By default there are two components active:

- ``multi user channel (XEP-0045)`` config for group channel functions
- ``http_upload (XEP-0363)`` enables upload via http(s) for clients to share files.

To disable this components set the corresponding state to ``false``.
See :envvar:`prosody__default_components`.

For example, to disable ``http_upload (XEP-0363)``:

.. code-block:: yaml
   :emphasize-lines: 3

   prosody__host_components:
     'upload.{{ prosody__domain }}':
       enabled: false



Domains
~~~~~~~

The default virtual host uses :envvar:`prosody__domain` as domain.

The components uses two subdomains:

- ``conference.{{ prosody__domain }}``
- ``upload.{{ prosody__domain }}``.

Ports
~~~~~

By default the ports are:

- `5222` (c2s)
- `5269` (s2s)
- `5280` http
- `5281` https



Example inventory
-----------------

To enable Prosody server support on a host, it needs to be included in the Ansible inventory in a specific group:

.. code-block:: none

   [debops_service_prosody]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prosody`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/prosody.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prosody``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::ferm``
  Role tag for configure the firewall ferm.
